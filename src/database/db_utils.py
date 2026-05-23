import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.config.setting import DB_PATH

DIAS_NOME = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_classes_today():
    """Retorna as aulas de hoje (seg-sex). Fim de semana retorna as da próxima segunda."""
    day_of_week = datetime.now().weekday()

    if day_of_week >= 5:
        day_of_week = 0
        prefixo = "Hoje é fim de semana. Aulas da próxima segunda-feira"
    else:
        prefixo = f"Aulas de hoje ({DIAS_NOME[day_of_week]})"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.nome, h.hora_inicio, h.hora_fim, d.sala, d.professor
        FROM horarios h
        JOIN disciplinas d ON h.disciplina_id = d.id
        WHERE h.dia_semana = ?
        ORDER BY h.hora_inicio
    ''', (day_of_week,))
    rows = cursor.fetchall()
    conn.close()

    return {"info": prefixo, "aulas": [dict(r) for r in rows]}

def get_classes_this_week():
    """Retorna todas as aulas da semana (seg-sex) com nome do dia."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.dia_semana, d.nome, h.hora_inicio, h.hora_fim, d.sala, d.professor
        FROM horarios h
        JOIN disciplinas d ON h.disciplina_id = d.id
        WHERE h.dia_semana BETWEEN 0 AND 4
        ORDER BY h.dia_semana, h.hora_inicio
    ''')
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['dia_nome'] = DIAS_NOME[d['dia_semana']]
        result.append(d)
    return result

def get_upcoming_exams(days=7):
    """Retorna provas nos próximos X dias."""
    today       = datetime.now().strftime('%Y-%m-%d')
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.data, d.nome AS disciplina, p.descricao
        FROM provas p
        JOIN disciplinas d ON p.disciplina_id = d.id
        WHERE p.data BETWEEN ? AND ?
        ORDER BY p.data
    ''', (today, future_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_pending_tasks():
    """Retorna tarefas pendentes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT titulo, descricao, data_entrega, prioridade
        FROM tarefas
        WHERE status = 'pendente'
        ORDER BY data_entrega ASC, prioridade DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_agenda_item(tipo, titulo, descricao, data, disciplina_nome=None, hora_inicio=None, hora_fim=None, sala=None, dia_semana=None):
    """
    Insere um item na agenda.
    tipo='prova'    → tabela provas  (requer data, disciplina_nome)
    tipo='tarefa'   → tabela tarefas (requer titulo, data opcional)
    tipo='horario'  → tabela horarios (requer disciplina_nome, dia_semana, hora_inicio, hora_fim)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if tipo == 'tarefa':
        cursor.execute(
            'INSERT INTO tarefas (titulo, descricao, data_entrega, status, prioridade) VALUES (?, ?, ?, ?, ?)',
            (titulo, descricao or '', data, 'pendente', 1)
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Tarefa '{titulo}' adicionada."}

    # Para prova e horário precisamos do id da disciplina
    if not disciplina_nome:
        conn.close()
        return {"status": "erro", "mensagem": "Nome da disciplina é obrigatório para provas e horários."}

    cursor.execute(
        'SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)',
        (disciplina_nome,)
    )
    row = cursor.fetchone()
    if not row:
        # Lista disciplinas disponíveis para ajudar o usuário
        cursor.execute('SELECT nome FROM disciplinas ORDER BY nome')
        disponiveis = [r['nome'] for r in cursor.fetchall()]
        conn.close()
        return {
            "status": "erro",
            "mensagem": f"Disciplina '{disciplina_nome}' não encontrada. Disponíveis: {disponiveis}"
        }
    disciplina_id = row['id']

    if tipo == 'prova':
        if not data:
            conn.close()
            return {"status": "erro", "mensagem": "Data é obrigatória para provas."}
        cursor.execute(
            'INSERT INTO provas (disciplina_id, data, descricao) VALUES (?, ?, ?)',
            (disciplina_id, data, descricao or titulo)
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Prova de '{disciplina_nome}' em {data} adicionada."}

    if tipo == 'horario':
        if dia_semana is None or not hora_inicio or not hora_fim:
            conn.close()
            return {"status": "erro", "mensagem": "dia_semana, hora_inicio e hora_fim são obrigatórios para horários."}
        cursor.execute(
            'INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, hora_fim) VALUES (?, ?, ?, ?)',
            (disciplina_id, dia_semana, hora_inicio, hora_fim)
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Horário de '{disciplina_nome}' adicionado."}

    conn.close()
    return {"status": "erro", "mensagem": f"Tipo '{tipo}' inválido. Use: tarefa, prova ou horario."}

if __name__ == "__main__":
    print("Aulas de hoje:", get_classes_today())
    print("Semana:", get_classes_this_week())
    print("Próximas provas:", get_upcoming_exams())
    print("Tarefas pendentes:", get_pending_tasks())