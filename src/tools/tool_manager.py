from src.tools.tools import (
    consultar_agenda,
    consultar_semana,
    adicionar_na_agenda,
    listar_tarefas,
    adicionar_tarefa,
    concluir_tarefa,
    buscar_material_rag,
    adicionar_materia,
    sair_da_materia,
    listar_materias,
)
from src.utils.logger import registrar_tool


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

    elif tool_name == "adicionar_materia":
        resultado = adicionar_materia(
            nome       = argumentos.get("nome"),
            professor  = argumentos.get("professor", ""),
            sala       = argumentos.get("sala", ""),
        )

    elif tool_name == "sair_da_materia":
        resultado = sair_da_materia(
            nome = argumentos.get("nome")
        )

    elif tool_name == "listar_materias":
        resultado = listar_materias()

    else:
        resultado = {"erro": f"Ferramenta '{tool_name}' não encontrada."}

    registrar_tool(
        nome_ferramenta=tool_name,
        entrada=argumentos,
        saida=resultado
    )
    return resultado