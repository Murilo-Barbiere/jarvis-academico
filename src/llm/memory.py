from typing import List, Dict

class ChatMemoryManager:
    """
    Gerencia a memória de curto prazo (Chat History) do JARVIS Acadêmico.
    Mantém um buffer deslizante de interações para preservar o contexto.
    """
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico (user ou assistant)."""
        self.history.append({"role": role, "content": content})
        
        # Mantém o limite de mensagens (removendo as mais antigas se necessário)
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def get_history(self) -> List[Dict[str, str]]:
        """Retorna o histórico atual das mensagens."""
        return self.history

    def clear(self):
        """Limpa o histórico de conversas."""
        self.history = []
