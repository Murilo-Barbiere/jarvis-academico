from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def perguntar_llm(mensagem: str, contexto: str):

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente que responde chamado "
                        "usando o contexto enviado."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
                    CONTEXTO:
                    {contexto}

                    PERGUNTA:
                    {mensagem}
                    """
                }
            ],)

        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar LLM: {str(e)}"