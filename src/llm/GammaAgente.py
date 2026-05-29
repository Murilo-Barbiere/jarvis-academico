from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from src.llm.SYSTEM_PROMPT import SYSTEM_PROMPT

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
    
def decidir_tool(mensagem):
    resposta = client.chat.completions.create(
        model=os.getenv("MODEL"),

        response_format={"type": "json_object"},

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {   
                "role": "user",
                "content": mensagem
            }
        ],
        temperature=0)

    conteudo = resposta.choices[0].message.content

    try:
        return json.loads(conteudo)
    except:
        return None