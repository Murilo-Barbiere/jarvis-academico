import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.config.setting import DB_PATH

def seed_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    disciplinas = [
        ('Inteligência Artificial', 'Prof. Alan Turing', 'Sala 101'),
        ('Estrutura de Dados', 'Prof. Grace Hopper', 'Sala 202'),
        ('Banco de Dados', 'Prof. Edgar Codd', 'Sala 303'),
        ('Redes de Computadores', 'Prof. Vint Cerf', 'Sala 404'),
        ('Engenharia de Software', 'Prof. Margaret Hamilton', 'Sala 505')
    ]
    cursor.executemany('INSERT INTO disciplinas (nome, professor, sala) VALUES (?, ?, ?)', disciplinas)
    
    horarios = [
        (1, 0, '19:00', '20:40'), # IA - Segunda
        (1, 2, '19:00', '20:40'), # IA - Quarta
        (2, 1, '19:00', '20:40'), # ED - Terça
        (2, 3, '19:00', '20:40'), # ED - Quinta
        (3, 4, '19:00', '22:30'), # BD - Sexta
        (4, 0, '20:50', '22:30'), # Redes - Segunda
        (4, 2, '20:50', '22:30'), # Redes - Quarta
        (5, 1, '20:50', '22:30'), # Eng. Soft - Terça
        (5, 3, '20:50', '22:30')  # Eng. Soft - Quinta
    ]
    cursor.executemany('INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, hora_fim) VALUES (?, ?, ?, ?)', horarios)

    hoje = datetime.now().strftime('%Y-%m-%d')
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    proxima_semana = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    provas = [
        (1, amanha, 'P1 de Inteligência Artificial'),
        (2, '2026-06-15', 'Trabalho de Estrutura de Dados'),
        (3, '2026-06-20', 'Prova Final de Banco de Dados'),
        (4, proxima_semana, 'Teste de Redes'),
        (5, '2026-07-01', 'Projeto de Engenharia de Software')
    ]
    cursor.executemany('INSERT INTO provas (disciplina_id, data, descricao) VALUES (?, ?, ?)', provas)

    tarefas = [
        ('Estudar para prova de IA', 'Revisar Redes Neurais', amanha, 'pendente', 3),
        ('Implementar Árvore B', 'Projeto de ED', '2026-06-10', 'pendente', 2),
        ('Ler artigo de RAG', 'Opcional', None, 'pendente', 1),
        ('Configurar Roteador', 'Laboratório de Redes', proxima_semana, 'pendente', 2),
        ('Diagrama de Classes', 'Trabalho de Eng. Soft', '2026-06-05', 'pendente', 3),
        ('Revisar SQL', 'Exercícios de BD', hoje, 'concluído', 1)
    ]
    cursor.executemany('INSERT INTO tarefas (titulo, descricao, data_entrega, status, prioridade) VALUES (?, ?, ?, ?, ?)', tarefas)

    conn.commit()
    conn.close()
    print("Dados de exemplo inseridos com sucesso.")

if __name__ == "__main__":
    seed_db()
