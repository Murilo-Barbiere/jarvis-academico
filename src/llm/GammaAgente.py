from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import Optional, Dict, Any

from src.llm.SYSTEM_PROMPT import SYSTEM_PROMPT
from src.llm.memory import ChatMemoryManager
from src.utils.logger import configurar_logger

load_dotenv()
logger = configurar_logger()

PLANO_ESTUDOS_SYSTEM_PROMPT = """
Você é o JARVIS Acadêmico, especialista em planejamento de estudos universitários.

Com base no contexto fornecido, crie um plano de estudos personalizado com:
1. Situação geral — resumo dos prazos críticos
2. Prioridades de hoje — o que estudar agora e por quê
3. Plano por disciplina — tópicos-chave do material RAG + tempo sugerido proporcional aos dias restantes
4. Tarefas urgentes — integradas ao plano
5. Dica motivacional — curta e objetiva

REGRAS:
- Use dias_restantes de cada prova para priorizar
- Se houver materiais_rag, mencione os tópicos específicos encontrados
- Se não houver materiais_rag, sugira estratégias gerais pela disciplina
- Responda em Português (Brasil)

CONTEXTO:
{contexto}
"""

class JarvisAgent:
    """
    Classe principal do Agente JARVIS Acadêmico.
    Orquestra a memória, o tool calling e a geração de respostas.
    """
    def __init__(self, model: Optional[str] = None):
        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("API_KEY")
        )
        self.model = model or os.getenv("MODEL")
        self.memory = ChatMemoryManager(max_messages=10)
        self.system_prompt = SYSTEM_PROMPT

    def _get_messages_for_llm(self, user_query: Optional[str] = None, system_override: Optional[str] = None) -> list:
        """Constrói a lista de mensagens incluindo o prompt do sistema e o histórico."""
        messages = [
            {"role": "system", "content": system_override or self.system_prompt}
        ]
        
        # Adiciona o histórico de conversas
        messages.extend(self.memory.get_history())
        
        # Adiciona a pergunta atual se fornecida
        if user_query:
            messages.append({"role": "user", "content": user_query})
            
        return messages

    def decidir_tool(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Decide qual ferramenta utilizar com base no histórico e na query atual.
        """
        messages = self._get_messages_for_llm(user_query)
        
        try:
            resposta = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=0
            )
            
            conteudo = resposta.choices[0].message.content
            return json.loads(conteudo)
        except Exception as e:
            # Em caso de erro, podemos logar e retornar None para o fluxo seguir sem tool
            logger.error(f"Erro ao decidir tool: {str(e)}")
            return None

    def gerar_resposta_final(self, user_query: str, contexto: str) -> str:
        """
        Gera a resposta final para o usuário utilizando o contexto obtido (RAG ou Tool).
        """
        # Prompt específico para síntese da resposta com contexto
        system_sintese = (
            "Você é o JARVIS Acadêmico. Responda o usuário de forma amigável "
            "e objetiva, utilizando o contexto fornecido abaixo para embasar sua resposta.\n\n"
            f"CONTEXTO ATUAL:\n{contexto}"
        )
        
        messages = self._get_messages_for_llm(user_query, system_override=system_sintese)
        
        try:
            resposta = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            conteudo_resposta = resposta.choices[0].message.content
            
            # Atualiza a memória com a interação completa
            self.memory.add_message("user", user_query)
            self.memory.add_message("assistant", conteudo_resposta)
            
            return conteudo_resposta
        except Exception as e:
            return f"Erro ao gerar resposta final: {str(e)}"

    def gerar_plano_estudos(self, user_query: str, contexto: str) -> str:
        """
        Gera um plano de estudos personalizado com base no contexto acadêmico e RAG.
        """
        system = PLANO_ESTUDOS_SYSTEM_PROMPT.format(contexto=contexto)
        
        messages = self._get_messages_for_llm(user_query, system_override=system)
        
        try:
            resposta = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            
            conteudo_resposta = resposta.choices[0].message.content
            
            # Atualiza a memória com a interação completa
            self.memory.add_message("user", user_query)
            self.memory.add_message("assistant", conteudo_resposta)
            
            return conteudo_resposta
        except Exception as e:
            logger.error(f"Erro ao gerar plano de estudos: {e}")
            return self.gerar_resposta_final(user_query, contexto)

# Mantendo compatibilidade com funções existentes se necessário,
# mas encorajando o uso da classe JarvisAgent.
_instancia_global = None

def get_agent():
    global _instancia_global
    if _instancia_global is None:
        _instancia_global = JarvisAgent()
    return _instancia_global

def perguntar_llm(mensagem: str, contexto: str):
    return get_agent().gerar_resposta_final(mensagem, contexto)

def decidir_tool(mensagem: str):
    return get_agent().decidir_tool(mensagem)
