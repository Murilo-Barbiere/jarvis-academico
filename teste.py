from openai import OpenAI

client = OpenAI(base_url='https://llm.liaufms.org/v1/qwen2-5-14b-instruct-awq',
                 api_key='REIkURcI7rTTqsTwlJi8MrgnKFwOiqky7Ezh7hH-l-k')

resp = client.chat.completions.create(
    model='Qwen/Qwen2.5-14B-Instruct-AWQ',
    messages=[{'role': 'user', 'content': 'Hi'}],
)

print(resp.choices[0].message.content)