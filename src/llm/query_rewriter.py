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
            "Você é um motor de reescrita de consultas (Query Rewriter).\n"
            "Sua tarefa é transformar a entrada do usuário em uma consulta otimizada para busca semântica (RAG) e acionamento de ferramentas.\n\n"
            "DIRETRIZES CRÍTICAS:\n"
            "1. NÃO responda à pergunta do usuário.\n"
            "2. NÃO inicie uma conversa ou peça esclarecimentos.\n"
            "3. NÃO inclua explicações, notas ou metadados na resposta.\n"
            "4. Saída exclusivamente em PORTUGUÊS (Brasil).\n"
            "5. Se a consulta for simples e clara, retorne-a IDENTICA.\n"
            "6. Preserve nomes próprios, datas e termos técnicos.\n\n"
            "EXEMPLOS:\n"
            "Usuário: 'oq tem pra hoje?'\n"
            "Rewriter: 'quais são as aulas, tarefas e provas agendadas para hoje?'\n\n"
            "Usuário: 'quais tarefas eu ainda tenho?'\n"
            "Rewriter: 'listar todas as tarefas pendentes'\n\n"
            "Usuário: 'quem é o prof de eda?'\n"
            "Rewriter: 'quem é o professor da disciplina Estrutura de Dados?'\n\n"
            "Usuário: 'o que é um grafo?'\n"
            "Rewriter: 'definição e conceito de grafos em computação'\n\n"
            "REPOSTA ESPERADA: Apenas o texto da consulta reformulada, sem aspas."
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
