from src.tools.tools import (
    consultar_agenda,
    consultar_semana,
    adicionar_na_agenda,
    listar_tarefas,
    adicionar_tarefa,
    concluir_tarefa,
    buscar_material_rag,
)
from src.tools.tool_logger import registrar_log


def executar_tool(tool_name, argumentos, vetor_store=None):

    resultado = None

    if tool_name == "consultar_agenda":
        resultado = consultar_agenda()

    elif tool_name == "consultar_semana":
        resultado = consultar_semana()

    elif tool_name == "adicionar_na_agenda":
        resultado = adicionar_na_agenda(
            tipo        = argumentos.get("tipo"),
            titulo      = argumentos.get("titulo", ""),
            descricao   = argumentos.get("descricao", ""),
            data        = argumentos.get("data"),
            disciplina  = argumentos.get("disciplina"),
            hora_inicio = argumentos.get("hora_inicio"),
            hora_fim    = argumentos.get("hora_fim"),
            dia_semana  = argumentos.get("dia_semana"),
        )

    elif tool_name == "listar_tarefas":
        resultado = listar_tarefas()

    elif tool_name == "adicionar_tarefa":
        resultado = adicionar_tarefa(
            titulo       = argumentos.get("titulo"),
            descricao    = argumentos.get("descricao", ""),
            data_entrega = argumentos.get("data_entrega"),
        )

    elif tool_name == "concluir_tarefa":
        resultado = concluir_tarefa(titulo=argumentos.get("titulo"))

    elif tool_name == "buscar_material_rag":
        pergunta = argumentos.get("pergunta") or argumentos.get("query") or "consulta vazia"
        resultado = buscar_material_rag(vetor_store, pergunta)

    else:
        resultado = {"erro": f"Ferramenta '{tool_name}' não encontrada."}

    registrar_log(nome_ferramenta=tool_name, entrada=argumentos, saida=resultado)
    return resultado