
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json

def main():
    from src.utils.logger import configurar_logger
    logger = configurar_logger()
    logger.info("Aplicação JARVIS Acadêmico iniciada")

    from src.llm.GammaAgente import get_agent
    from src.rag.VetorStore import VetorStore
    from src.config.setting import MODEL_NAME, PDF_PATH, VECTOR_STORE_PATH
    from src.rag.chunker import preparar_documentos
    from src.rag.loader import ler_pdfs
    from src.tools.tool_manager import executar_tool

    jarvis = get_agent()
    
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

        # 1. Agente decide o que fazer (Tool Calling com Histórico)
        plano = jarvis.decidir_tool(query)
        
        lista_tools = plano.get("tools", [])
        resultados_acumulados = []
        
        tool_especial = "nenhuma"

        # 2. Execução Sequencial das Tools com Resiliência
        if lista_tools:
            for item in lista_tools:
                nome_tool = item.get("tool")
                argumentos = item.get("arguments", {})
                
                if nome_tool == "nenhuma" or not nome_tool:
                    continue
                
                logger.info(f"Executando ferramenta: {nome_tool}")
                
                try:
                    # Executa a tool
                    resultado = executar_tool(nome_tool, argumentos, vetor_store)
                    resultados_acumulados.append({
                        "tool": nome_tool,
                        "status": "sucesso",
                        "resultado": resultado
                    })
                    logger.info(f"Ferramenta {nome_tool} executada com sucesso")
                    
                    # Identifica tools que mudam o fluxo de resposta final
                    # Quiz tem precedência sobre Plano de Estudos
                    if nome_tool == "iniciar_quiz":
                        tool_especial = "iniciar_quiz"
                    elif nome_tool == "encerrar_quiz":
                        tool_especial = "encerrar_quiz"
                    elif nome_tool == "planejar_estudos" and tool_especial not in ["iniciar_quiz", "encerrar_quiz"]:
                        tool_especial = "planejar_estudos"

                except Exception as e:
                    logger.error(f"Erro na execução da tool {nome_tool}: {e}")
                    resultados_acumulados.append({
                        "tool": nome_tool,
                        "status": "erro",
                        "mensagem": str(e)
                    })

            contexto = json.dumps(resultados_acumulados, ensure_ascii=False, default=str)
        else:
            logger.info("Nenhuma ferramenta necessária. Usando apenas histórico/conhecimento.")
            contexto = "Nenhuma informação extra necessária além do histórico da conversa."

        # 3. Geração da Resposta Final (com síntese e atualização da memória)
        if tool_especial == "planejar_estudos":
            resposta = jarvis.gerar_plano_estudos(query, contexto)
        elif tool_especial == "iniciar_quiz":
            resposta = jarvis.iniciar_quiz(query, contexto)
        elif tool_especial == "encerrar_quiz":
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
