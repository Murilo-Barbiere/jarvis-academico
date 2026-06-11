from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import Optional, Dict, Any

from src.llm.SYSTEM_PROMPT import SYSTEM_PROMPT
from src.llm.memory import ChatMemoryManager

load_dotenv()

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
            print(f"Erro ao decidir tool: {str(e)}")
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
