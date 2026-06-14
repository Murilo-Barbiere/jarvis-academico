from datetime import datetime
from src.database.db_utils import (
    get_classes_today,
    get_upcoming_exams,
    get_upcoming_assignments,
    get_pending_tasks
)
from src.utils.logger import configurar_logger

logger = configurar_logger()

class StudyPlannerService:
    def __init__(self, vetor_store=None):
        self.vetor_store = vetor_store

    def montar_contexto(self, exam_window_days=14) -> dict:
        """
        Executa a coleta de dados e busca RAG para montar o contexto do plano de estudos.
        """
        # Etapa 1 — coleta dados acadêmicos
        agenda_hoje = get_classes_today()
        provas_raw = get_upcoming_exams(days=exam_window_days)
        trabalhos_raw = get_upcoming_assignments(days=exam_window_days)
        tarefas_raw = get_pending_tasks()

        hoje = datetime.now().date()
        
        # Calcula dias_restantes para cada prova
        provas = []
        for p in provas_raw:
            p_dict = dict(p)
            try:
                data_prova = datetime.strptime(p_dict['data'], '%Y-%m-%d').date()
                dias_restantes = (data_prova - hoje).days
                p_dict['dias_restantes'] = dias_restantes
            except (ValueError, KeyError):
                p_dict['dias_restantes'] = 999
            provas.append(p_dict)

        # Calcula dias_restantes para cada trabalho
        trabalhos = []
        for t in trabalhos_raw:
            t_dict = dict(t)
            try:
                data_entrega = datetime.strptime(t_dict['data_entrega'], '%Y-%m-%d').date()
                dias_restantes = (data_entrega - hoje).days
                t_dict['dias_restantes'] = dias_restantes
            except (ValueError, KeyError):
                t_dict['dias_restantes'] = 999
            trabalhos.append(t_dict)
            
        # Ordena tarefas por data_entrega e prioridade
        tarefas = sorted(tarefas_raw, key=lambda x: (x.get('data_entrega') or '9999-12-31', -(x.get('prioridade') or 0)))

        # Etapa 2 — busca RAG por disciplina
        materiais_rag = {}
        disciplinas_com_material = []
        
        # Combina provas e trabalhos urgentes para busca RAG
        entregas_urgentes = sorted(provas + trabalhos, key=lambda x: x['dias_restantes'])[:3]
        
        if self.vetor_store and entregas_urgentes:
            for item in entregas_urgentes:
                disciplina = item.get('disciplina', 'Desconhecida')
                descricao = item.get('descricao', '')
                query = f"conteúdo e tópicos de {disciplina}: {descricao}"
                
                if disciplina in materiais_rag:
                    continue

                try:
                    resultados = self.vetor_store.buscar(query, top_k=4)
                    if resultados:
                        materiais_rag[disciplina] = [
                            {
                                "texto": r["texto"],
                                "fonte": r["arquivo"],
                                "relevancia": r["similaridade"]
                            }
                            for r in resultados
                        ]
                        disciplinas_com_material.append(disciplina)
                except Exception as e:
                    logger.error(f"Erro ao buscar RAG para {disciplina}: {e}")

        # Etapa 3 — monta e retorna este dict
        return {
            "tipo": "plano_estudos",
            "data_hoje": datetime.now().strftime("%d/%m/%Y (%A)"),
            "agenda_hoje": agenda_hoje,
            "provas": provas,
            "trabalhos": trabalhos,
            "tarefas": tarefas,
            "materiais_rag": materiais_rag,
            "resumo_meta": {
                "total_provas": len(provas),
                "total_trabalhos": len(trabalhos),
                "total_tarefas": len(tarefas),
                "disciplinas_com_material": disciplinas_com_material
            }
        }
