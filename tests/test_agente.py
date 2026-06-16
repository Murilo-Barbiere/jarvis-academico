from src.llm.GammaAgente import decidir_tool


def test_decidir_tool_argumentos():
    resposta = decidir_tool(
        "adicione uma tarefa chamada trabalho de banco"
    )
    assert "tools" in resposta
    assert len(resposta["tools"]) > 0
    assert "arguments" in resposta["tools"][0]


def test_decidir_tool_listar():
    resposta = decidir_tool(
        "quais tarefas eu tenho?"
    )
    assert any(t["tool"] == "listar_tarefas" for t in resposta["tools"])


def test_decidir_tool_tarefa():
    resposta = decidir_tool(
        "crie uma tarefa chamada estudar IA"
    )
    assert any(t["tool"] == "adicionar_tarefa" for t in resposta["tools"])


def test_json_valido():
    resposta = decidir_tool(
        "listar tarefas"
    )
    assert isinstance(resposta, dict)
    assert "tools" in resposta


from src.llm.GammaAgente import perguntar_llm

def test_perguntar_llm():
    resposta = perguntar_llm(
        mensagem="O que é IA?",
        contexto="IA significa inteligência artificial."
    )
    assert isinstance(resposta, str)
    assert len(resposta) > 0


def test_sem_tool():
    resposta = decidir_tool(
        "oi tudo bem?"
    )
    assert not resposta.get("tools")
