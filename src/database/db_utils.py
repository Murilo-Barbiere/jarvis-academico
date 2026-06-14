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

def get_upcoming_assignments(days=7):
    """Retorna trabalhos/entregas nos próximos X dias."""
    today       = datetime.now().strftime('%Y-%m-%d')
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.data_entrega, d.nome AS disciplina, t.descricao
        FROM trabalhos t
        JOIN disciplinas d ON t.disciplina_id = d.id
        WHERE t.data_entrega BETWEEN ? AND ?
        ORDER BY t.data_entrega
    ''', (today, future_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_assignments():
    """Retorna todos os trabalhos cadastrados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.data_entrega, d.nome AS disciplina, t.descricao
        FROM trabalhos t
        JOIN disciplinas d ON t.disciplina_id = d.id
        ORDER BY t.data_entrega
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_exams():
    """Retorna todas as provas cadastradas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.data, d.nome AS disciplina, p.descricao
        FROM provas p
        JOIN disciplinas d ON p.disciplina_id = d.id
        ORDER BY p.data
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_pending_tasks():
    """Retorna tarefas pendentes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT titulo, descricao, data_entrega
        FROM tarefas
        WHERE status = 'pendente'
        ORDER BY data_entrega ASC
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
            'INSERT INTO tarefas (titulo, descricao, data_entrega, status) VALUES (?, ?, ?, ?)',
            (titulo, descricao or '', data, 'pendente')
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

    if tipo == 'trabalho':
        if not data:
            conn.close()
            return {"status": "erro", "mensagem": "Data de entrega é obrigatória para trabalhos."}
        cursor.execute(
            'INSERT INTO trabalhos (disciplina_id, data_entrega, descricao) VALUES (?, ?, ?)',
            (disciplina_id, data, descricao or titulo)
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Trabalho de '{disciplina_nome}' para {data} adicionado."}

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
def add_disciplina(nome, professor=None, sala=None):
    """Adiciona uma nova disciplina."""
    
    if not nome or not nome.strip():
        return {
            "status": "erro",
            "mensagem": "Nome da disciplina é obrigatório."
        }

    nome = nome.strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)",
        (nome,)
    )

    if cursor.fetchone():
        conn.close()
        return {
            "status": "erro",
            "mensagem": f"Disciplina '{nome}' já existe."
        }

    cursor.execute(
        '''
        INSERT INTO disciplinas (nome, professor, sala)
        VALUES (?, ?, ?)
        ''',
        (nome, professor or "", sala or "")
    )

    conn.commit()
    conn.close()

    return {
        "status": "sucesso",
        "mensagem": f"Disciplina '{nome}' adicionada."
    }


def remove_disciplina(nome):
    """Remove uma disciplina pelo nome."""

    if not nome or not nome.strip():
        return {
            "status": "erro",
            "mensagem": "Nome da disciplina é obrigatório."
        }

    nome = nome.strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)",
        (nome,)
    )

    row = cursor.fetchone()

    if not row:
        cursor.execute("SELECT nome FROM disciplinas ORDER BY nome")
        disponiveis = [r["nome"] for r in cursor.fetchall()]

        conn.close()

        return {
            "status": "erro",
            "mensagem": f"Disciplina '{nome}' não encontrada. Disponíveis: {disponiveis}"
        }

    disciplina_id = row["id"]

    # remove dependências
    cursor.execute(
        "DELETE FROM horarios WHERE disciplina_id = ?",
        (disciplina_id,)
    )

    cursor.execute(
        "DELETE FROM provas WHERE disciplina_id = ?",
        (disciplina_id,)
    )

    cursor.execute(
        "DELETE FROM trabalhos WHERE disciplina_id = ?",
        (disciplina_id,)
    )

    # remove disciplina
    cursor.execute(
        "DELETE FROM disciplinas WHERE id = ?",
        (disciplina_id,)
    )

    conn.commit()
    conn.close()

    return {
        "status": "sucesso",
        "mensagem": f"Disciplina '{nome}' removida."
    }


if __name__ == "__main__":
    print("Aulas de hoje:", get_classes_today())
    print("Semana:", get_classes_this_week())
    print("Próximas provas:", get_upcoming_exams())
    print("Próximos trabalhos:", get_upcoming_assignments())
    print("Tarefas pendentes:", get_pending_tasks())

def get_disciplinas():
    """Retorna todas as disciplinas cadastradas."""

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT nome, professor, sala
        FROM disciplinas
        ORDER BY nome
        '''
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]

def update_horario(disciplina_nome, dia_semana_antigo, novo_dia_semana=None, nova_hora_inicio=None, nova_hora_fim=None):
    """
    Altera o horário de uma disciplina existente.
    """
    if not disciplina_nome:
        return {"status": "erro", "mensagem": "Nome da disciplina é obrigatório."}

    if dia_semana_antigo is None:
        return {"status": "erro", "mensagem": "Dia da semana antigo é obrigatório para identificar o horário."}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar ID da disciplina
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        cursor.execute('SELECT nome FROM disciplinas ORDER BY nome')
        disponiveis = [r['nome'] for r in cursor.fetchall()]
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada. Disponíveis: {disponiveis}"}

    disciplina_id = row['id']

    # Verificar se o horário antigo existe
    cursor.execute('''
        SELECT id FROM horarios 
        WHERE disciplina_id = ? AND dia_semana = ?
    ''', (disciplina_id, dia_semana_antigo))
    horario_row = cursor.fetchone()
    if not horario_row:
        conn.close()
        return {"status": "erro", "mensagem": f"Não foi encontrado um horário para '{disciplina_nome}' no dia {dia_semana_antigo}."}

    horario_id = horario_row['id']

    # Montar update dinâmico
    updates = []
    params = []
    if novo_dia_semana is not None:
        updates.append("dia_semana = ?")
        params.append(novo_dia_semana)
    if nova_hora_inicio:
        updates.append("hora_inicio = ?")
        params.append(nova_hora_inicio)
    if nova_hora_fim:
        updates.append("hora_fim = ?")
        params.append(nova_hora_fim)

    if not updates:
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum dado para alterar foi fornecido."}

    params.append(horario_id)
    query = f"UPDATE horarios SET {', '.join(updates)} WHERE id = ?"

    try:
        cursor.execute(query, params)
        conn.commit()
        return {"status": "sucesso", "mensagem": f"Horário de '{disciplina_nome}' alterado com sucesso."}
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao atualizar horário: {str(e)}"}
    finally:
        conn.close()

def get_completed_tasks():
    """Retorna tarefas concluídas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT titulo, descricao, data_entrega
        FROM tarefas
        WHERE status = 'concluido'
        ORDER BY data_entrega DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def remove_task(titulo):
    """Remove uma tarefa pelo título."""
    if not titulo:
        return {"status": "erro", "mensagem": "Título é obrigatório."}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE LOWER(titulo) = LOWER(?)", (titulo,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    
    if count > 0:
        return {"status": "sucesso", "mensagem": f"Tarefa '{titulo}' removida."}
    return {"status": "erro", "mensagem": f"Tarefa '{titulo}' não encontrada."}

def update_task(titulo, nova_descricao=None, nova_data_entrega=None):
    """Atualiza uma tarefa existente."""
    if not titulo:
        return {"status": "erro", "mensagem": "Título é obrigatório."}

    updates = []
    params = []
    if nova_descricao is not None:
        updates.append("descricao = ?")
        params.append(nova_descricao)
    if nova_data_entrega is not None:
        updates.append("data_entrega = ?")
        params.append(nova_data_entrega)

    if not updates:
        return {"status": "erro", "mensagem": "Nenhum dado para alteração fornecido."}

    params.append(titulo)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tarefas SET {', '.join(updates)} WHERE LOWER(titulo) = LOWER(?)", params)
    conn.commit()
    count = cursor.rowcount
    conn.close()

    if count > 0:
        return {"status": "sucesso", "mensagem": f"Tarefa '{titulo}' atualizada."}
    return {"status": "erro", "mensagem": f"Tarefa '{titulo}' não encontrada."}

def remove_exam(disciplina_nome, data):
    """Remove uma prova de uma disciplina em uma data específica."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada."}
    
    cursor.execute("DELETE FROM provas WHERE disciplina_id = ? AND data = ?", (row['id'], data))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    
    if count > 0:
        return {"status": "sucesso", "mensagem": f"Prova de '{disciplina_nome}' em {data} removida."}
    return {"status": "erro", "mensagem": "Prova não encontrada com esses critérios."}

def update_exam(disciplina_nome, data_antiga, nova_data=None, nova_descricao=None):
    """Atualiza data ou descrição de uma prova."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada."}
    
    updates = []
    params = []
    if nova_data:
        updates.append("data = ?")
        params.append(nova_data)
    if nova_descricao is not None:
        updates.append("descricao = ?")
        params.append(nova_descricao)
        
    if not updates:
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum dado para alteração fornecido."}

    params.extend([row['id'], data_antiga])
    cursor.execute(f"UPDATE provas SET {', '.join(updates)} WHERE disciplina_id = ? AND data = ?", params)
    conn.commit()
    count = cursor.rowcount
    conn.close()

    if count > 0:
        return {"status": "sucesso", "mensagem": f"Prova de '{disciplina_nome}' atualizada."}
    return {"status": "erro", "mensagem": "Prova não encontrada."}

def remove_assignment(disciplina_nome, data_entrega):
    """Remove um trabalho."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada."}
    
    cursor.execute("DELETE FROM trabalhos WHERE disciplina_id = ? AND data_entrega = ?", (row['id'], data_entrega))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    
    if count > 0:
        return {"status": "sucesso", "mensagem": f"Trabalho de '{disciplina_nome}' para {data_entrega} removido."}
    return {"status": "erro", "mensagem": "Trabalho não encontrado."}

def update_assignment(disciplina_nome, data_antiga, nova_data=None, nova_descricao=None):
    """Atualiza um trabalho."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada."}
    
    updates = []
    params = []
    if nova_data:
        updates.append("data_entrega = ?")
        params.append(nova_data)
    if nova_descricao is not None:
        updates.append("descricao = ?")
        params.append(nova_descricao)
        
    if not updates:
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum dado para alteração fornecido."}

    params.extend([row['id'], data_antiga])
    cursor.execute(f"UPDATE trabalhos SET {', '.join(updates)} WHERE disciplina_id = ? AND data_entrega = ?", params)
    conn.commit()
    count = cursor.rowcount
    conn.close()

    if count > 0:
        return {"status": "sucesso", "mensagem": f"Trabalho de '{disciplina_nome}' atualizado."}
    return {"status": "erro", "mensagem": "Trabalho não encontrado."}

def remove_horario(disciplina_nome, dia_semana, hora_inicio):
    """Remove um horário específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM disciplinas WHERE LOWER(nome) = LOWER(?)', (disciplina_nome,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "erro", "mensagem": f"Disciplina '{disciplina_nome}' não encontrada."}
    
    cursor.execute("DELETE FROM horarios WHERE disciplina_id = ? AND dia_semana = ? AND hora_inicio = ?", 
                   (row['id'], dia_semana, hora_inicio))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    
    if count > 0:
        return {"status": "sucesso", "mensagem": f"Horário de '{disciplina_nome}' removido."}
    return {"status": "erro", "mensagem": "Horário não encontrado."}

def update_disciplina(nome_antigo, novo_nome=None, novo_professor=None, nova_sala=None):
    """Atualiza dados da disciplina."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    if novo_nome:
        updates.append("nome = ?")
        params.append(novo_nome)
    if novo_professor is not None:
        updates.append("professor = ?")
        params.append(novo_professor)
    if nova_sala is not None:
        updates.append("sala = ?")
        params.append(nova_sala)

    if not updates:
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum dado para alteração fornecido."}

    params.append(nome_antigo)
    cursor.execute(f"UPDATE disciplinas SET {', '.join(updates)} WHERE LOWER(nome) = LOWER(?)", params)
    conn.commit()
    count = cursor.rowcount
    conn.close()

    if count > 0:
        return {"status": "sucesso", "mensagem": f"Disciplina '{nome_antigo}' atualizada."}
    return {"status": "erro", "mensagem": f"Disciplina '{nome_antigo}' não encontrada."}