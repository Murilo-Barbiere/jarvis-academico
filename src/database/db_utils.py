import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.config.setting import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_classes_today():
    """Retorna as aulas de hoje."""
    day_of_week = datetime.now().weekday()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT d.nome, h.hora_inicio, h.hora_fim, d.sala, d.professor
    FROM horarios h
    JOIN disciplinas d ON h.disciplina_id = d.id
    WHERE h.dia_semana = ?
    ORDER BY h.hora_inicio
    '''
    cursor.execute(query, (day_of_week,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_classes_this_week():
    """Retorna todas as aulas da semana atual."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT h.dia_semana, d.nome, h.hora_inicio, h.hora_fim, d.sala
    FROM horarios h
    JOIN disciplinas d ON h.disciplina_id = d.id
    ORDER BY h.dia_semana, h.hora_inicio
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_upcoming_exams(days=7):
    """Retorna provas nos próximos X dias."""
    today = datetime.now().strftime('%Y-%m-%d')
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT p.data, d.nome as disciplina, p.descricao
    FROM provas p
    JOIN disciplinas d ON p.disciplina_id = d.id
    WHERE p.data BETWEEN ? AND ?
    ORDER BY p.data
    '''
    cursor.execute(query, (today, future_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_pending_tasks():
    """Retorna tarefas pendentes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT titulo, descricao, data_entrega, prioridade
    FROM tarefas
    WHERE status = 'pendente'
    ORDER BY data_entrega ASC, prioridade DESC
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    print("Aulas de hoje:", get_classes_today())
    print("Próximas provas:", get_upcoming_exams())
    print("Tarefas pendentes:", get_pending_tasks())
