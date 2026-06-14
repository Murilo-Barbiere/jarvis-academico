import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.config.setting import DB_PATH

def seed_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Idempotente: só insere se ainda não houver disciplinas
    cursor.execute('SELECT COUNT(*) FROM disciplinas')
    if cursor.fetchone()[0] > 0:
        print("Banco já possui dados. Seed ignorado.")
        conn.close()
        return

    disciplinas = [
        ('Inteligência Artificial', 'Prof. Alan Turing', 'Sala 101'),
        ('Estrutura de Dados', 'Prof. Grace Hopper', 'Sala 202'),
        ('Banco de Dados', 'Prof. Edgar Codd', 'Sala 303'),
        ('Redes de Computadores', 'Prof. Vint Cerf', 'Sala 404'),
        ('Engenharia de Software', 'Prof. Margaret Hamilton', 'Sala 505')
    ]
    cursor.executemany(
        'INSERT INTO disciplinas (nome, professor, sala) VALUES (?, ?, ?)',
        disciplinas
    )

    # Busca os IDs reais recém-inseridos para garantir consistência do JOIN
    cursor.execute('SELECT id, nome FROM disciplinas ORDER BY id')
    id_map = {nome: id_ for id_, nome in cursor.fetchall()}

    ia  = id_map['Inteligência Artificial']
    ed  = id_map['Estrutura de Dados']
    bd  = id_map['Banco de Dados']
    rd  = id_map['Redes de Computadores']
    es  = id_map['Engenharia de Software']

    # dia_semana: 0=seg, 1=ter, 2=qua, 3=qui, 4=sex  (padrão datetime.weekday())
    horarios = [
        (ia, 0, '19:00', '20:40'),  # IA - Segunda
        (ia, 2, '19:00', '20:40'),  # IA - Quarta
        (ed, 1, '19:00', '20:40'),  # ED - Terça
        (ed, 3, '19:00', '20:40'),  # ED - Quinta
        (bd, 4, '19:00', '22:30'),  # BD - Sexta
        (rd, 0, '20:50', '22:30'),  # Redes - Segunda
        (rd, 2, '20:50', '22:30'),  # Redes - Quarta
        (es, 1, '20:50', '22:30'),  # Eng. Soft - Terça
        (es, 3, '20:50', '22:30'),  # Eng. Soft - Quinta
    ]
    cursor.executemany(
        'INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, hora_fim) VALUES (?, ?, ?, ?)',
        horarios
    )

    amanha        = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    proxima_semana = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    provas = [
        (ia, amanha,         'P1 de Inteligência Artificial'),
        (bd, '2026-06-20',   'Prova Final de Banco de Dados'),
        (rd, proxima_semana, 'Teste de Redes'),
    ]
    cursor.executemany(
        'INSERT INTO provas (disciplina_id, data, descricao) VALUES (?, ?, ?)',
        provas
    )

    trabalhos = [
        (ed, '2026-06-15',   'Trabalho de Estrutura de Dados'),
        (es, '2026-07-01',   'Projeto de Engenharia de Software'),
    ]
    cursor.executemany(
        'INSERT INTO trabalhos (disciplina_id, data_entrega, descricao) VALUES (?, ?, ?)',
        trabalhos
    )

    hoje  = datetime.now().strftime('%Y-%m-%d')
    tarefas = [
        ('Estudar para prova de IA', 'Revisar Redes Neurais', amanha,         'pendente',  3),
        ('Implementar Árvore B',     'Projeto de ED',         '2026-06-10',   'pendente',  2),
        ('Ler artigo de RAG',        'Opcional',               None,          'pendente',  1),
        ('Configurar Roteador',      'Laboratório de Redes',  proxima_semana, 'pendente',  2),
        ('Diagrama de Classes',      'Trabalho de Eng. Soft', '2026-06-05',   'pendente',  3),
        ('Revisar SQL',              'Exercícios de BD',       hoje,          'concluido', 1),
    ]
    cursor.executemany(
        'INSERT INTO tarefas (titulo, descricao, data_entrega, status, prioridade) VALUES (?, ?, ?, ?, ?)',
        tarefas
    )

    conn.commit()
    conn.close()
    print("Dados de exemplo inseridos com sucesso.")

if __name__ == "__main__":
    seed_db()