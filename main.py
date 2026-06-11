import sys
from src.rag.chunker import preparar_documentos
from src.rag.loader import ler_pdfs
from src.llm.GammaAgente import get_agent
from src.config.setting import MODEL_NAME, PDF_PATH
from src.rag.VetorStore import VetorStore
from src.utils.logger import configurar_logger
from src.tools.tool_manager import executar_tool

def main():
    logger = configurar_logger()
    logger.info("Aplicação JARVIS Acadêmico iniciada")

    # Inicialização do Agente (Stateful)
    jarvis = get_agent()

    # Preparação do RAG
    documentos = ler_pdfs(PDF_PATH)
    if not documentos:
        print("Aviso: Nenhum documento PDF encontrado para o RAG.")
        vetor_store = None
    else:
        chunks, metadados = preparar_documentos(documentos)
        vetor_store = VetorStore(MODEL_NAME)
        vetor_store.adicionar_documentos(chunks, metadados)
        logger.info("Vector Store carregada com sucesso")

    print("\n=== JARVIS Acadêmico Pronto ===")
    print("Digite 'sair' para encerrar ou 'limpar' para resetar a memória.")

    while True:
        query = input("\nVocê: ")

        if query.lower() == "sair":
            logger.info("Sistema encerrado pelo usuário")
            break
        
        if query.lower() == "limpar":
            jarvis.memory.clear()
            print("Histórico de conversa limpo!")
            continue

        logger.info(f"Processando query: {query}")

        # 1. Agente decide o que fazer (Tool Calling com Histórico)
        plano = jarvis.decidir_tool(query)
        
        contexto = ""
        nome_tool = plano.get("tool") if plano else "nenhuma"

        # 2. Execução da Tool ou Fluxo Direto
        if nome_tool and nome_tool != "nenhuma":
            argumentos = plano.get("arguments", {})
            logger.info(f"Executando ferramenta: {nome_tool}")
            
            try:
                # Caso especial para RAG que precisa do vetor_store
                resultado = executar_tool(nome_tool, argumentos, vetor_store)
                contexto = str(resultado)
                logger.info("Ferramenta executada com sucesso")
            except Exception as e:
                logger.error(f"Erro na execução da tool: {e}")
                contexto = f"Erro ao processar sua solicitação na ferramenta {nome_tool}: {e}"
        else:
            # Se 'nenhuma' tool foi escolhida, o contexto é vazio (ou o histórico basta)
            logger.info("Nenhuma ferramenta necessária. Usando apenas histórico/conhecimento.")
            contexto = "Nenhuma informação extra necessária além do histórico da conversa."

        # 3. Geração da Resposta Final (com síntese e atualização da memória)
        resposta = jarvis.gerar_resposta_final(query, contexto)
        
        print(f"\nJARVIS: {resposta}")

if __name__ == "__main__":
    main()
