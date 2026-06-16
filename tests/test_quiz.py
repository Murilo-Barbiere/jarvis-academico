import os
import sys
import json
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.GammaAgente import get_agent

def test_quiz_completo():
    load_dotenv()
    agent = get_agent()
    
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
        
        # Teste de decisão de tool
        decisao = agent.decidir_tool(query)
        tools = decisao.get("tools", [])
        print(f"  Tools: {[t.get('tool') for t in tools]}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_quiz_completo()
