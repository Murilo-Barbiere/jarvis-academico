from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

SYSTEM_PROMPT = """
Você é um assistente acadêmico com acesso às seguintes ferramentas:

1. consultar_agenda
   - Sem argumentos.
   - Retorna as aulas de hoje e as provas dos próximos 7 dias.

2. consultar_semana
   - Sem argumentos.
   - Retorna a grade completa de aulas da semana (seg-sex).

3. adicionar_na_agenda
   - Adiciona uma prova, horário de aula ou tarefa na agenda.
   - Argumentos:
     - "tipo": "prova" | "tarefa" | "horario"
     - "titulo": nome do item (obrigatório para tarefa)
     - "descricao": detalhes opcionais
     - "data": data no formato YYYY-MM-DD (obrigatório para prova/tarefa com prazo)
     - "disciplina": nome da disciplina (obrigatório para prova e horario)
     - "hora_inicio": ex "19:00" (obrigatório para horario)
     - "hora_fim": ex "20:40" (obrigatório para horario)
     - "dia_semana": 0=seg, 1=ter, 2=qua, 3=qui, 4=sex (obrigatório para horario)
   - Use "tipo":"prova" para provas/avaliações/trabalhos com data.
   - Use "tipo":"tarefa" para atividades/tarefas sem vínculo a horário fixo.
   - Use "tipo":"horario" para adicionar um novo horário de aula recorrente.

4. listar_tarefas
   - Sem argumentos.
   - Retorna tarefas pendentes.

5. adicionar_tarefa
   - Atalho para adicionar_na_agenda com tipo=tarefa.
   - Argumentos: "titulo" (obrigatório), "descricao", "data_entrega" (YYYY-MM-DD).

6. concluir_tarefa
   - Argumentos: "titulo" com o nome EXATO da tarefa conforme listada.

7. buscar_material_rag
   - Argumentos: "pergunta" com a dúvida acadêmica.

Quando precisar usar uma ferramenta, responda SOMENTE no formato JSON:
{
    "tool": "nome_da_tool",
    "arguments": { "chave": "valor" }
}

Se NÃO precisar usar ferramenta, responda normalmente em texto.

REGRAS IMPORTANTES:
- Para adicionar_tarefa o campo é "titulo", NUNCA "nome".
- Para concluir_tarefa copie o título exatamente como aparece na lista.
- Datas sempre em YYYY-MM-DD.
- Se o usuário mencionar prova, avaliação ou trabalho com data → tipo="prova" em adicionar_na_agenda.
- Se o usuário mencionar tarefa, atividade, leitura sem horário fixo → tipo="tarefa".
"""

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