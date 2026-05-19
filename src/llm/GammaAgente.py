from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def perguntar_llm(mensagem: str, contexto: str):

    prompt = f"""
Use o contexto abaixo para responder a pergunta.

CONTEXTO:
{contexto}

PERGUNTA:
{mensagem}
"""

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro ao consultar LLM: {str(e)}"