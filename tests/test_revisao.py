import sys
import os
import json
from unittest.mock import MagicMock

# Ajusta o path para importar os módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.llm.Agente import JarvisAgent
from src.tools.tools import montar_revisao

def test_montar_revisao_logic():
    print("\n=== TESTE LÓGICA MONTAR REVISAO ===")
    
    # Simula histórico com pontos fracos
    historico = [
        {"role": "user", "content": "Pergunta do quiz..."},
        {"role": "assistant", "content": "### Avaliação\nIncorreta.\n\n### Pontos Fracos / Lacunas de Conhecimento\n- Protocolo TCP e handshaking\n\n### Recomendação de Revisão\nReleia kurose-tcp.pdf\n\n### Próxima Pergunta\nO que é UDP?"}
    ]
    
    # Mock do VetorStore
    mock_vs = MagicMock()
    mock_vs.buscar.return_value = [{"texto": "Conteúdo sobre TCP...", "arquivo": "kurose-tcp.pdf", "similaridade": 0.9}]
    
    resultado = montar_revisao(mock_vs, historico)
    
    print(f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
    assert resultado["status"] == "sucesso"
    assert "TCP" in resultado["ponto_fraco"]
    assert len(resultado["contexto_rag"]) > 0
    print("✓ Lógica da tool ok.")

def test_agente_decisao_revisao():
    print("\n=== TESTE DECISÃO DO AGENTE PARA REVISÃO ===")
    agent = JarvisAgent()
    
    # Simula histórico onde o quiz acabou e o agente ofereceu revisão
    agent.memory.add_message("assistant", "### Avaliação\n...### Pontos Fracos\n- DNS Recursivo\n...")
    agent.memory.add_message("assistant", "Modo Quiz finalizado! Gostaria de uma revisão?")
    
    # Pergunta que deve acionar a tool
    query = "Sim, por favor"
    
    plano = agent.decidir_tool(query)
    print(f"Plano para '{query}': {plano}")
    
    nometool = plano["tools"][0]["tool"] if plano["tools"] else None
    assert nometool == "montar_revisao"
    print("✓ Gatilho de decisão ok.")

if __name__ == "__main__":
    try:
        test_montar_revisao_logic()
        test_agente_decisao_revisao()
        print("\nTESTES CONCLUÍDOS COM SUCESSO!")
    except Exception as e:
        print(f"\nERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
