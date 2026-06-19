from llm.Agente import decidir_tool

def test_alterar_horario_acionada():
    """Testa se a tool alterar_horario é acionada corretamente."""
    frase = "o horário da disciplina de Cálculo mudou, agora é na terça às 14:00"
    resposta = decidir_tool(frase)
    
    assert any(t["tool"] == "alterar_horario" for t in resposta["tools"])
    tool = next(t for t in resposta["tools"] if t["tool"] == "alterar_horario")
    assert "disciplina" in tool["arguments"]
    # Se o LLM inferir que mudou PARA terça, novo_dia_semana deve estar lá
    assert "novo_dia_semana" in tool["arguments"] or "hora_inicio" in tool["arguments"]

def test_alterar_horario_argumentos_especificos():
    """Testa se os argumentos são extraídos corretamente."""
    frase = "mude o horário de IA de segunda para quarta às 10:00"
    resposta = decidir_tool(frase)
    
    assert any(t["tool"] == "alterar_horario" for t in resposta["tools"])
    tool = next(t for t in resposta["tools"] if t["tool"] == "alterar_horario")
    args = tool["arguments"]
    assert args["disciplina"].lower() == "ia"
    assert args["dia_semana"] == 0 # Segunda
    assert args["novo_dia_semana"] == 2 # Quarta
    assert args["hora_inicio"] == "10:00"
