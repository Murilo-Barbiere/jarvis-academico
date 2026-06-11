import unittest
from unittest.mock import MagicMock, patch
from src.llm.query_rewriter import QueryRewriterService

class TestQueryRewriterService(unittest.TestCase):
    def setUp(self):
        self.rewriter = QueryRewriterService()

    @patch('openai.resources.chat.completions.Completions.create')
    def test_rewrite_success(self, mock_create):
        # Configura o mock para retornar uma resposta de sucesso
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "O que é uma árvore binária de busca?"
        mock_create.return_value = mock_response

        query = "arv busca bin"
        resultado = self.rewriter.rewrite(query)

        self.assertEqual(resultado, "O que é uma árvore binária de busca?")
        mock_create.assert_called_once()

    @patch('openai.resources.chat.completions.Completions.create')
    def test_rewrite_failure_returns_original(self, mock_create):
        # Configura o mock para lançar uma exceção
        mock_create.side_effect = Exception("Erro na API")

        query = "pergunta importante"
        resultado = self.rewriter.rewrite(query)

        # Deve retornar a query original em caso de erro
        self.assertEqual(resultado, query)

    def test_rewrite_empty_query(self):
        # Consulta vazia não deve nem chamar a API
        resultado = self.rewriter.rewrite("")
        self.assertEqual(resultado, "")

        resultado = self.rewriter.rewrite("   ")
        self.assertEqual(resultado, "   ")

    @patch('openai.resources.chat.completions.Completions.create')
    def test_rewrite_already_optimized(self, mock_create):
        # Simula que a LLM retorna a mesma coisa ou algo muito similar
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Quais são as minhas tarefas para hoje?"
        mock_create.return_value = mock_response

        query = "Quais são as minhas tarefas para hoje?"
        resultado = self.rewriter.rewrite(query)

        self.assertEqual(resultado, "Quais são as minhas tarefas para hoje?")

if __name__ == '__main__':
    unittest.main()
