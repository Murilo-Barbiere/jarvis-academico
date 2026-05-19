#testa se a llm esta no ar de forma rapida sem esperar o Rag

from openai import OpenAI

client = OpenAI(base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A')
resp = client.chat.completions.create(
    model='google/gemma-3-12b-it',
    messages=[{'role': 'user', 'content': 'Hi'}],
)
print(resp.choices[0].message.content)