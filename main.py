import sys

from src.rag.chunker import preparar_documentos
from src.rag.context_builder import gerar_contexto
from src.rag.loader import ler_pdfs
from src.llm import GammaAgente as agente
from src.config.setting import MODEL_NAME, PDF_PATH
from src.rag.VetorStore import VetorStore
from src.utils.logger import configurar_logger


def main():
    logger = configurar_logger()

    logger.info("Aplicação iniciada")
    documentos = ler_pdfs(PDF_PATH)

    if not documentos:
        print("Nenhum documento encontrado.")
        logger.error(f"Nenhum documento encontrado no dataSete")
        sys.exit(1)

    chunks, metadados = preparar_documentos(documentos)
    logger.info(f"Total de chunks: {len(chunks)}\n")

    vetor_store = VetorStore(MODEL_NAME)
    vetor_store.adicionar_documentos(chunks,metadados)
    logger.info("Vector Store criada com sucesso")
  
    while True:
        query = input("\nPergunta: ")

        if query.lower() == "sair": 
            logger.info("Sistema encerrar")
            break

        logger.info(f"Query: {query}")

        resultados = vetor_store.buscar(query)
        logger.info(f"Chunks recuperados: {len(resultados)}")

        for i, item in enumerate(resultados, start=1):
            logger.info(f"[Chunk {i}] arquivo={item['arquivo']}")

        contexto = gerar_contexto(resultados) 

        resposta = agente.perguntar_llm(query,contexto)
        logger.info(f"Resposta gerada | tamanho={len(resposta)}")

        print("\n\n--------------------Resposta--------------------")
        print(resposta)

if __name__ == "__main__":
    main()