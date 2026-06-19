import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from llm.Agente import decidir_tool
from src.tools.tools import obter_resumo_academico

def test_obter_resumo_academico_estrutura():
    resultado = obter_resumo_academico()
    assert resultado["status"] == "sucesso"
    assert "tarefas_pendentes" in resultado
    assert "provas_proximos_30_dias" in resultado
    assert "trabalhos_proximos_30_dias" in resultado
    assert "agenda_hoje" in resultado
    assert "materiais_disponiveis" in resultado

def test_trigger_resumo_para_plano():
    pergunta = "Monte um plano de estudos para a prova de amanhã"
    resposta = decidir_tool(pergunta)
    assert any(t["tool"] == "planejar_estudos" for t in resposta["tools"])

def test_trigger_resumo_para_prioridade():
    pergunta = "O que devo priorizar hoje?"
    resposta = decidir_tool(pergunta)
    # obter_resumo_academico é usado para visão geral e prioridades rápidas
    assert any(t["tool"] == "obter_resumo_academico" for t in resposta["tools"])

def test_trigger_resumo_para_situacao_geral():
    pergunta = "Como está minha situação acadêmica?"
    resposta = decidir_tool(pergunta)
    assert any(t["tool"] == "obter_resumo_academico" for t in resposta["tools"])
