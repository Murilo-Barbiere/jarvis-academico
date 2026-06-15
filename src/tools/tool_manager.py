from src.rag.context_builder import gerar_contexto
from src.tools.tools import (
    consultar_agenda,
    consultar_semana,
    adicionar_na_agenda,
    alterar_horario,
    listar_tarefas,
    listar_trabalhos,
    listar_provas,
    adicionar_tarefa,
    concluir_tarefa,
    buscar_material_rag,
    adicionar_materia,
    sair_da_materia,
    listar_materias,
    obter_resumo_academico,
    remover_tarefa,
    alterar_tarefa,
    listar_tarefas_concluidas,
    remover_prova,
    remover_trabalho,
    alterar_prova,
    alterar_trabalho,
    remover_horario_tool,
    alterar_materia_tool,
)
from src.tools.study_planner import StudyPlannerService
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

    elif tool_name == "alterar_horario":
        resultado = alterar_horario(
            disciplina      = argumentos.get("disciplina"),
            dia_semana      = argumentos.get("dia_semana"),
            novo_dia_semana = argumentos.get("novo_dia_semana"),
            hora_inicio     = argumentos.get("hora_inicio"),
            hora_fim        = argumentos.get("hora_fim"),
        )

    elif tool_name == "listar_tarefas":
        resultado = listar_tarefas()

    elif tool_name == "listar_trabalhos":
        resultado = listar_trabalhos()

    elif tool_name == "listar_provas":
        resultado = listar_provas()

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
        raw_results = buscar_material_rag(vetor_store, pergunta)
        resultado = gerar_contexto(raw_results)

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

    elif tool_name == "obter_resumo_academico":
        arquivos = []
        if vetor_store and hasattr(vetor_store, 'metadados'):
            arquivos = list(set([m['arquivo'] for m in vetor_store.metadados]))
        resultado = obter_resumo_academico(materiais=arquivos)

    elif tool_name == "remover_tarefa":
        resultado = remover_tarefa(titulo=argumentos.get("titulo"))

    elif tool_name == "alterar_tarefa":
        resultado = alterar_tarefa(
            titulo       = argumentos.get("titulo"),
            descricao    = argumentos.get("descricao"),
            data_entrega = argumentos.get("data_entrega"),
        )

    elif tool_name == "listar_tarefas_concluidas":
        resultado = listar_tarefas_concluidas()

    elif tool_name == "remover_prova":
        resultado = remover_prova(
            disciplina = argumentos.get("disciplina"),
            data       = argumentos.get("data"),
        )

    elif tool_name == "remover_trabalho":
        resultado = remover_trabalho(
            disciplina   = argumentos.get("disciplina"),
            data_entrega = argumentos.get("data_entrega"),
        )

    elif tool_name == "alterar_prova":
        resultado = alterar_prova(
            disciplina     = argumentos.get("disciplina"),
            data_antiga    = argumentos.get("data_antiga"),
            nova_data      = argumentos.get("nova_data"),
            nova_descricao = argumentos.get("nova_descricao"),
        )

    elif tool_name == "alterar_trabalho":
        resultado = alterar_trabalho(
            disciplina     = argumentos.get("disciplina"),
            data_antiga    = argumentos.get("data_antiga"),
            nova_data      = argumentos.get("nova_data"),
            nova_descricao = argumentos.get("nova_descricao"),
        )

    elif tool_name == "remover_horario":
        resultado = remover_horario_tool(
            disciplina  = argumentos.get("disciplina"),
            dia_semana  = argumentos.get("dia_semana"),
            hora_inicio = argumentos.get("hora_inicio"),
        )

    elif tool_name == "alterar_materia":
        resultado = alterar_materia_tool(
            nome      = argumentos.get("nome"),
            professor = argumentos.get("professor"),
            sala      = argumentos.get("sala"),
        )

    elif tool_name == "planejar_estudos":
        planner = StudyPlannerService(vetor_store=vetor_store)
        resultado = planner.montar_contexto()

    elif tool_name == "iniciar_quiz":
        topico = argumentos.get("topico") or "estudo geral"
        if vetor_store:
            resultado = buscar_material_rag(vetor_store, topico)
        else:
            resultado = {"erro": "Vector store não disponível para gerar quiz."}

    else:
        resultado = {"erro": f"Ferramenta '{tool_name}' não encontrada."}

    registrar_tool(
        nome_ferramenta=tool_name,
        entrada=argumentos,
        saida=resultado
    )
    return resultado