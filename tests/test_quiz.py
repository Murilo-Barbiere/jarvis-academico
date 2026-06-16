import os
import sys
import json
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.GammaAgente import get_agent
from src.llm.query_rewriter import QueryRewriterService

def test_quiz_completo():
    load_dotenv()
    agent = get_agent()
    rewriter = QueryRewriterService()
    
    queries = [
        "Me faça um quiz sobre DNS",
        "Pode me testar sobre Tabelas de Espalhamento?",
        "Quero perguntas de revisão sobre HTTP",
        "Me desafie com perguntas sobre redes",
        "parar quiz",
        "sair do quiz",
        "chega de perguntas por hoje"
    ]
    
    print(f"=== TESTE COMPLETO DE QUIZ ===")
    print(f"Modelo: {os.getenv('MODEL')}\n")
    
    for query in queries:
        print(f"USUÁRIO: '{query}'")
        
        # 1. Teste sem Rewriter
        decisao_direta = agent.decidir_tool(query)
        tools_direto = decisao_direta.get("tools", [])
        print(f"  [Direto]   Tools: {[t.get('tool') for t in tools_direto]}")
        
        # 2. Teste com Rewriter
        query_reformulada = rewriter.rewrite(query)
        decisao_rewriter = agent.decidir_tool(query_reformulada)
        tools_rewriter = decisao_rewriter.get("tools", [])
        print(f"  [Rewriter] Query: '{query_reformulada}'")
        print(f"  [Rewriter] Tools: {[t.get('tool') for t in tools_rewriter]}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_quiz_completo()
