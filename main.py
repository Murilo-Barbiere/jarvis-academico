
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json

def main():
    from src.utils.logger import configurar_logger
    logger = configurar_logger()
    logger.info("Aplicação JARVIS Acadêmico iniciada")

    from src.llm.GammaAgente import get_agent
    from src.llm.query_rewriter import QueryRewriterService
    from src.rag.VetorStore import VetorStore
    from src.config.setting import MODEL_NAME, PDF_PATH, JARVIS_QUERY_REWRITER_ENABLED, VECTOR_STORE_PATH
    from src.rag.chunker import preparar_documentos
    from src.rag.loader import ler_pdfs
    from src.tools.tool_manager import executar_tool

    jarvis = get_agent()
    
    rewriter = QueryRewriterService()

    vetor_store = VetorStore(MODEL_NAME)
    
    if not vetor_store.carregar(VECTOR_STORE_PATH):
        logger.info("Índice não encontrado ou inválido. Reconstruindo...")
        documentos = ler_pdfs(PDF_PATH)
        if not documentos:
            print("Aviso: Nenhum documento PDF encontrado para o RAG.")
            vetor_store = None
        else:
            chunks, metadados = preparar_documentos(documentos)
            vetor_store.adicionar_documentos(chunks, metadados)
            vetor_store.salvar(VECTOR_STORE_PATH)
            logger.info("Vector Store criada e salva com sucesso")
    else:
        logger.info(f"Índice carregado: {len(vetor_store.chunks)} chunks")

    print("\n=== JARVIS Acadêmico Pronto ===")
    print("Digite '/sair' para encerrar ou '/limpar' para resetar a memória.")

    while True:
        query = input("\nVocê: ")

        if query.lower() == "/sair":
            logger.info("Sistema encerrado pelo usuário")
            break
        
        if query.lower() == "/limpar":
            jarvis.memory.clear()
            print("Histórico de conversa limpo!")
            continue

        logger.info(f"Processando query: {query}")

        # Camada de Query Rewriting
        query_para_agente = query
        if JARVIS_QUERY_REWRITER_ENABLED:
            query_para_agente = rewriter.rewrite(query)

        # 1. Agente decide o que fazer (Tool Calling com Histórico)
        plano = jarvis.decidir_tool(query_para_agente)
        
        contexto = ""
        nome_tool = plano.get("tool") if plano else "nenhuma"

        # 2. Execução da Tool ou Fluxo Direto
        if nome_tool and nome_tool != "nenhuma":
            argumentos = plano.get("arguments", {})
            logger.info(f"Executando ferramenta: {nome_tool}")
            
            try:
                # Caso especial para RAG que precisa do vetor_store
                resultado = executar_tool(nome_tool, argumentos, vetor_store)
                contexto = json.dumps(resultado, ensure_ascii=False, default=str)
                logger.info("Ferramenta executada com sucesso")
            except Exception as e:
                logger.error(f"Erro na execução da tool: {e}")
                contexto = f"Erro ao processar sua solicitação na ferramenta {nome_tool}: {e}"
        else:
            # Se 'nenhuma' tool foi escolhida, o contexto é vazio (ou o histórico basta)
            logger.info("Nenhuma ferramenta necessária. Usando apenas histórico/conhecimento.")
            contexto = "Nenhuma informação extra necessária além do histórico da conversa."

        # 3. Geração da Resposta Final (com síntese e atualização da memória)
        if nome_tool == "planejar_estudos":
            resposta = jarvis.gerar_plano_estudos(query, contexto)
        elif nome_tool == "iniciar_quiz":
            resposta = jarvis.iniciar_quiz(query, contexto)
        elif nome_tool == "encerrar_quiz":
            resposta = jarvis.encerrar_quiz()
        else:
            resposta = jarvis.gerar_resposta_final(query, contexto)
        
        print(f"\nJARVIS: {resposta}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
