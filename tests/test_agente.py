from src.llm.GammaAgente import decidir_tool


def test_decidir_tool_argumentos():

    resposta = decidir_tool(
        "adicione uma tarefa chamada trabalho de banco"
    )

    assert "arguments" in resposta

from src.llm.GammaAgente import decidir_tool


def test_decidir_tool_listar():

    resposta = decidir_tool(
        "quais tarefas eu tenho?"
    )

    assert resposta["tool"] == "listar_tarefas"

from src.llm.GammaAgente import decidir_tool


def test_decidir_tool_tarefa():

    resposta = decidir_tool(
        "crie uma tarefa chamada estudar IA"
    )

    assert resposta["tool"] == "adicionar_tarefa"

from src.llm.GammaAgente import decidir_tool


def test_json_valido():

    resposta = decidir_tool(
        "listar tarefas"
    )

    assert isinstance(resposta, dict)

from src.llm.GammaAgente import perguntar_llm

def test_perguntar_llm():

    resposta = perguntar_llm(
        mensagem="O que é IA?",
        contexto="IA significa inteligência artificial."
    )

    assert isinstance(resposta, str)

    assert len(resposta) > 0

from src.llm.GammaAgente import decidir_tool


def test_sem_tool():

    resposta = decidir_tool(
        "oi tudo bem?"
    )

    assert (
        resposta is None
        or "tool" not in resposta
        or resposta["tool"] == "nenhuma"
    )
