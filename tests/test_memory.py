import pytest
from src.llm.memory import ChatMemoryManager

def test_init():
    """Verifica se a memória é inicializada corretamente."""
    memory = ChatMemoryManager(max_messages=5)
    assert memory.max_messages == 5
    assert memory.history == []

def test_add_message():
    """Verifica a adição de uma única mensagem."""
    memory = ChatMemoryManager()
    memory.add_message("user", "Olá")
    history = memory.get_history()
    assert len(history) == 1
    assert history[0] == {"role": "user", "content": "Olá"}

def test_sliding_window():
    """Verifica se o limite de mensagens (sliding window) é respeitado."""
    max_msgs = 3
    memory = ChatMemoryManager(max_messages=max_msgs)
    
    mensagens = [
        ("user", "Msg 1"),
        ("assistant", "Resp 1"),
        ("user", "Msg 2"),
        ("assistant", "Resp 2")
    ]
    
    for role, content in mensagens:
        memory.add_message(role, content)
    
    history = memory.get_history()
    assert len(history) == max_msgs
    # Deve conter as 3 últimas mensagens
    assert history[0]["content"] == "Resp 1"
    assert history[1]["content"] == "Msg 2"
    assert history[2]["content"] == "Resp 2"

def test_clear_memory():
    """Verifica se a limpeza da memória funciona."""
    memory = ChatMemoryManager()
    memory.add_message("user", "Teste")
    memory.clear()
    assert memory.get_history() == []
    assert len(memory.get_history()) == 0

def test_default_max_messages():
    """Verifica se o valor padrão de max_messages é 10."""
    memory = ChatMemoryManager()
    assert memory.max_messages == 10

def test_message_order():
    """Verifica se a ordem das mensagens é preservada."""
    memory = ChatMemoryManager()
    memory.add_message("user", "Primeira")
    memory.add_message("assistant", "Segunda")
    memory.add_message("user", "Terceira")
    
    history = memory.get_history()
    assert [m["content"] for m in history] == ["Primeira", "Segunda", "Terceira"]

def test_empty_content():
    """Verifica se mensagens com conteúdo vazio são permitidas."""
    memory = ChatMemoryManager()
    memory.add_message("user", "")
    history = memory.get_history()
    assert history[0]["content"] == ""

def test_special_characters():
    """Verifica se caracteres especiais são preservados."""
    special_text = "Olá! Como vai? @#$%^&*() \n \t"
    memory = ChatMemoryManager()
    memory.add_message("user", special_text)
    history = memory.get_history()
    assert history[0]["content"] == special_text
