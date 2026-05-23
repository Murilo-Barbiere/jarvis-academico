import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db_utils import (
    get_classes_today,
    get_classes_this_week,
    get_pending_tasks,
    get_upcoming_exams,
    add_agenda_item,
    get_db_connection,
    add_disciplina,
    remove_disciplina,
    get_disciplinas,
)
# ── Agenda ────────────────────────────────────────────────────────────────────

def consultar_agenda():
    """Retorna aulas de hoje + próximas provas (7 dias)."""
    aulas  = get_classes_today()
    provas = get_upcoming_exams(days=7)
    return {"aulas": aulas, "provas_proximas": provas}

def consultar_semana():
    """Retorna a grade completa da semana."""
    return get_classes_this_week()

def adicionar_na_agenda(tipo, titulo, descricao="", data=None,
                        disciplina=None, hora_inicio=None,
                        hora_fim=None, dia_semana=None):
    """
    Adiciona um item na agenda.
    tipo: 'prova' | 'tarefa' | 'horario'
    """
    return add_agenda_item(
        tipo=tipo,
        titulo=titulo,
        descricao=descricao,
        data=data,
        disciplina_nome=disciplina,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        dia_semana=dia_semana,
    )

# ── Tarefas ───────────────────────────────────────────────────────────────────

def listar_tarefas():
    return get_pending_tasks()

def adicionar_tarefa(titulo, descricao="", data_entrega=None):
    if not titulo or not titulo.strip():
        return {"status": "erro", "mensagem": "O campo 'titulo' é obrigatório."}
    titulo = titulo.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM tarefas WHERE LOWER(titulo) = LOWER(?) AND status = 'pendente'",
        (titulo,)
    )
    if cursor.fetchone():
        conn.close()
        return {"status": "erro", "mensagem": f"Já existe uma tarefa pendente com o título '{titulo}'."}
    cursor.execute(
        "INSERT INTO tarefas (titulo, descricao, data_entrega) VALUES (?, ?, ?)",
        (titulo, descricao or "", data_entrega)
    )
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": f"Tarefa '{titulo}' adicionada."}

def concluir_tarefa(titulo):
    if not titulo or not titulo.strip():
        return {"status": "erro", "mensagem": "Título não informado."}
    titulo = titulo.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tarefas SET status = 'concluida' WHERE titulo = ? AND status = 'pendente'",
        (titulo,)
    )
    conn.commit()
    if cursor.rowcount == 0:
        cursor.execute(
            "UPDATE tarefas SET status = 'concluida' WHERE LOWER(titulo) = LOWER(?) AND status = 'pendente'",
            (titulo,)
        )
        conn.commit()
    linhas = cursor.rowcount
    if linhas == 0:
        disponiveis = [r['titulo'] for r in conn.execute(
            "SELECT titulo FROM tarefas WHERE status = 'pendente'"
        ).fetchall()]
        conn.close()
        return {"status": "erro", "mensagem": f"Tarefa '{titulo}' não encontrada. Pendentes: {disponiveis}"}
    conn.close()
    return {"status": "sucesso", "mensagem": f"Tarefa '{titulo}' concluída."}

def adicionar_materia(nome, professor="", sala=""):
    return add_disciplina(
        nome=nome,
        professor=professor,
        sala=sala
    )

def sair_da_materia(nome):
    return remove_disciplina(nome)

def listar_materias():
    return get_disciplinas()

# ── RAG ───────────────────────────────────────────────────────────────────────

def buscar_material_rag(vetor_store, pergunta):
    return vetor_store.buscar(pergunta)
    