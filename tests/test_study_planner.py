import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from src.tools.study_planner import StudyPlannerService

@patch('src.tools.study_planner.get_classes_today')
@patch('src.tools.study_planner.get_upcoming_exams')
@patch('src.tools.study_planner.get_pending_tasks')
def test_montar_contexto_chaves_obrigatorias(mock_tasks, mock_exams, mock_today):
    mock_today.return_value = {"aulas": []}
    mock_exams.return_value = []
    mock_tasks.return_value = []
    
    planner = StudyPlannerService()
    contexto = planner.montar_contexto()
    
    obrigatorias = ["tipo", "data_hoje", "agenda_hoje", "provas", "tarefas", "materiais_rag", "resumo_meta"]
    for chave in obrigatorias:
        assert chave in contexto

@patch('src.tools.study_planner.get_classes_today')
@patch('src.tools.study_planner.get_upcoming_exams')
@patch('src.tools.study_planner.get_pending_tasks')
def test_sem_vetor_store_materiais_vazio(mock_tasks, mock_exams, mock_today):
    mock_today.return_value = {"aulas": []}
    mock_exams.return_value = [{"disciplina": "Matematica", "data": "2026-06-20"}]
    mock_tasks.return_value = []
    
    planner = StudyPlannerService(vetor_store=None)
    contexto = planner.montar_contexto()
    
    assert contexto["materiais_rag"] == {}

@patch('src.tools.study_planner.get_classes_today')
@patch('src.tools.study_planner.get_upcoming_exams')
@patch('src.tools.study_planner.get_pending_tasks')
def test_com_vetor_store_mockado(mock_tasks, mock_exams, mock_today):
    mock_today.return_value = {"aulas": []}
    mock_exams.return_value = [{"disciplina": "IA", "data": "2026-06-20"}]
    mock_tasks.return_value = []
    
    mock_vs = MagicMock()
    mock_vs.buscar.return_value = [{"texto": "chunk 1", "arquivo": "doc.pdf", "similaridade": 0.9}]
    
    planner = StudyPlannerService(vetor_store=mock_vs)
    contexto = planner.montar_contexto()
    
    assert "IA" in contexto["materiais_rag"]
    assert len(contexto["materiais_rag"]["IA"]) == 1
    assert contexto["materiais_rag"]["IA"][0]["fonte"] == "doc.pdf"

@patch('src.tools.study_planner.get_classes_today')
@patch('src.tools.study_planner.get_upcoming_exams')
@patch('src.tools.study_planner.get_pending_tasks')
def test_calculo_dias_restantes(mock_tasks, mock_exams, mock_today):
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    mock_today.return_value = {"aulas": []}
    mock_exams.return_value = [{"disciplina": "Teste", "data": amanha}]
    mock_tasks.return_value = []
    
    planner = StudyPlannerService()
    contexto = planner.montar_contexto()
    
    # Busca a prova na lista de provas do contexto
    prova = next(p for p in contexto["provas"] if p["disciplina"] == "Teste")
    assert prova["dias_restantes"] == 1

@patch('src.tools.study_planner.get_classes_today')
@patch('src.tools.study_planner.get_upcoming_exams')
@patch('src.tools.study_planner.get_pending_tasks')
def test_limite_chamadas_rag(mock_tasks, mock_exams, mock_today):
    mock_today.return_value = {"aulas": []}
    # 5 provas
    mock_exams.return_value = [
        {"disciplina": f"D{i}", "data": (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')}
        for i in range(1, 6)
    ]
    mock_tasks.return_value = []
    
    mock_vs = MagicMock()
    mock_vs.buscar.return_value = []
    
    planner = StudyPlannerService(vetor_store=mock_vs)
    planner.montar_contexto()
    
    assert mock_vs.buscar.call_count == 3
