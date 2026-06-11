import time
import os
from openai import OpenAI
from dotenv import load_dotenv
from src.utils.logger import configurar_logger, registrar_query_rewriter

load_dotenv()
logger = configurar_logger()

class QueryRewriterService:
    """
    Serviço especializado em reformular consultas do usuário para otimizar
    a recuperação no RAG e a seleção de ferramentas pelo agente.
    """
    def __init__(self, model: str = None):
        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("API_KEY")
        )
        self.model = model or os.getenv("MODEL")
        self.system_prompt = (
            "Você é um especialista em reformulação de consultas para sistemas RAG e agentes com Tool Calling.\n\n"
            "Sua função NÃO é responder perguntas.\n\n"
            "Sua função é transformar a entrada do usuário em uma consulta mais clara, específica e adequada para:\n"
            "* recuperação de documentos (RAG)\n"
            "* seleção de ferramentas\n"
            "* planejamento de ações\n\n"
            "Regras:\n"
            "* Preserve a intenção original.\n"
            "* Não adicione fatos inexistentes.\n"
            "* Não responda à pergunta.\n"
            "* Retorne apenas a consulta reformulada.\n"
            "* Se a consulta já estiver boa, retorne-a praticamente inalterada."
        )

    def rewrite(self, user_query: str) -> str:
        """
        Reescreve a consulta do usuário. Caso falhe, retorna a original.
        """
        if not user_query or not user_query.strip():
            logger.warning("Consulta vazia recebida no QueryRewriterService.")
            return user_query

        start_time = time.time()
        try:
            resposta = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0
            )
            
            rewritten_query = resposta.choices[0].message.content.strip()
            
            # Remover possíveis aspas que o LLM pode colocar por engano
            if rewritten_query.startswith('"') and rewritten_query.endswith('"'):
                rewritten_query = rewritten_query[1:-1].strip()

            elapsed_time = time.time() - start_time
            
            registrar_query_rewriter(user_query, rewritten_query, elapsed_time)
            
            return rewritten_query
        except Exception as e:
            logger.error(f"Erro no QueryRewriterService: {e}")
            return user_query
