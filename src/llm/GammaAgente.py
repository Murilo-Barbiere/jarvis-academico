from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
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

        self.modo_quiz = False;
        self.contexto_quiz = "";

    def _get_messages_for_llm(self, user_query: Optional[str] = None, system_override: Optional[str] = None) -> list:
        """Constrói a lista de mensagens incluindo o prompt do sistema e o histórico."""
        agora = datetime.now()
        data_iso = agora.strftime("%Y-%m-%d")
        
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        
        dia_extenso = f"{dias_semana[agora.weekday()]}, {agora.day} de {meses[agora.month - 1]} de {agora.year}"

        system_base = system_override or self.system_prompt
        full_system_prompt = f"### DATA ATUAL: {data_iso} ({dia_extenso})\n\n{system_base}"

        messages = [
            {"role": "system", "content": full_system_prompt}
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
        if self.modo_quiz:
            system_sintese = (
                "Você é o JARVIS Acadêmico atuando no modo Quiz Interativo (Active Recall).\n"
                "O usuário está respondendo à pergunta que você fez anteriormente.\n\n"
                "SUA MISSÃO:\n"
                "1. Avalie a resposta do usuário comparando-a rigorosamente com o CONTEXTO DO QUIZ abaixo.\n"
                "2. Diga de forma clara se a resposta está Correta, Parcialmente Correta ou Incorreta (Avaliação).\n"
                "3. Identifique as dificuldades do usuário se ele errar ou esquecer conceitos centrais.\n"
                "4. Se a resposta não for totalmente correta, faça uma RECOMENDAÇÃO DE REVISÃO explícita baseada no contexto.\n"
                "5. Logo em seguida, apresente a PRÓXIMA pergunta para dar continuidade ao estudo.\n\n"
                f"CONTEXTO DO QUIZ:\n{self.contexto_quiz}"
            )
        else:
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

    def iniciar_quiz(self, user_query: str, contexto: str) -> str:
        """
        Inicia um quiz interativo com o usuário baseado no contexto fornecido.
        """
        self.modo_quiz = True
        self.contexto_quiz = contexto
        
        system_quiz_inicial = (
            "Você é o JARVIS Acadêmico. O usuário quer iniciar um Quiz Interativo (Active Recall).\n"
            "Com base estritamente no CONTEXTO RAG fornecido abaixo, formule a PRIMEIRA pergunta "
            "desafiadora sobre o material para testar o conhecimento do usuário. "
            "Não dê a resposta nem opções ainda, faça uma pergunta aberta!\n\n"
            f"CONTEXTO DO MATERIAL:\n{contexto}"
        )
        
        messages = self._get_messages_for_llm(user_query, system_override=system_quiz_inicial)
        logger.info("MODO QUIZ: Utilizando system_quiz_inicial para formular a primeira pergunta.")
        
        try:
            resposta = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5
            )
            
            conteudo_resposta = resposta.choices[0].message.content
            
            self.memory.add_message("user", user_query)
            self.memory.add_message("assistant", conteudo_resposta)
            
            return conteudo_resposta
        except Exception as e:
            logger.error(f"Erro ao iniciar quiz: {e}")
            return self.gerar_resposta_final(user_query, contexto)

    def encerrar_quiz(self) -> str:
        """
        Finaliza o modo quiz e reseta o estado.
        """
        self.modo_quiz = False
        self.contexto_quiz = ""
        logger.info("MODO QUIZ: Encerrado pelo usuário.")
        return "Modo Quiz finalizado! Como posso te ajudar agora?"

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
