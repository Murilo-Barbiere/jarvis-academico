import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.config.setting import DB_PATH

from src.utils.logger import configurar_logger

logger = configurar_logger()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        professor TEXT,
        sala TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disciplina_id INTEGER,
        dia_semana INTEGER NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fim TEXT NOT NULL,
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS provas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disciplina_id INTEGER,
        data TEXT NOT NULL,
        descricao TEXT,
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        data_entrega TEXT,
        status TEXT DEFAULT 'pendente',
        prioridade INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    logger.info(f"Banco de dados inicializado em {DB_PATH}")

if __name__ == "__main__":
    init_db()
