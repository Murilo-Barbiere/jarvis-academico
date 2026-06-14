from datetime import datetime
from src.database.db_utils import get_classes_today, get_upcoming_exams, get_pending_tasks
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
            
        # Ordena tarefas por data_entrega e prioridade
        tarefas = sorted(tarefas_raw, key=lambda x: (x.get('data_entrega') or '9999-12-31', -(x.get('prioridade') or 0)))

        # Etapa 2 — busca RAG por disciplina
        materiais_rag = {}
        disciplinas_com_material = []
        
        if self.vetor_store and provas:
            # Ordena provas por dias_restantes e pega no máximo 3 (as mais urgentes)
            provas_urgentes = sorted(provas, key=lambda x: x['dias_restantes'])[:3]
            
            for prova in provas_urgentes:
                disciplina = prova.get('disciplina', 'Desconhecida')
                descricao = prova.get('descricao', '')
                query = f"conteúdo e tópicos de {disciplina}: {descricao}"
                
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
            "tarefas": tarefas,
            "materiais_rag": materiais_rag,
            "resumo_meta": {
                "total_provas": len(provas),
                "total_tarefas": len(tarefas),
                "disciplinas_com_material": disciplinas_com_material
            }
        }
