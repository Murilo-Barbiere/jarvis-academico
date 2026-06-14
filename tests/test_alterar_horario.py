from src.llm.GammaAgente import decidir_tool

def test_alterar_horario_acionada():
    """Testa se a tool alterar_horario é acionada corretamente."""
    frase = "o horário da disciplina de Cálculo mudou, agora é na terça às 14:00"
    resposta = decidir_tool(frase)
    
    assert resposta["tool"] == "alterar_horario"
    assert "disciplina" in resposta["arguments"]
    assert "dia_semana" in resposta["arguments"] # Antigo (0-Seg provavelmente, mas o LLM pode inferir ou pedir)
    # Se o LLM inferir que mudou PARA terça, novo_dia_semana deve estar lá
    assert "novo_dia_semana" in resposta["arguments"] or "hora_inicio" in resposta["arguments"]

def test_alterar_horario_argumentos_especificos():
    """Testa se os argumentos são extraídos corretamente."""
    frase = "mude o horário de IA de segunda para quarta às 10:00"
    resposta = decidir_tool(frase)
    
    assert resposta["tool"] == "alterar_horario"
    args = resposta["arguments"]
    assert args["disciplina"].lower() == "ia"
    assert args["dia_semana"] == 0 # Segunda
    assert args["novo_dia_semana"] == 2 # Quarta
    assert args["hora_inicio"] == "10:00"
