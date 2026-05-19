#imports------------
import sys

import llm.GammaAgente as agente

from rag.rag import (
    VetorStore,
    gerar_contexto,
    ler_pdfs,
    preparar_documentos
)
from config.setting import MODEL_NAME, PDF_PATH

#imports------------


def main():
    # CARREGA PDFs
    print("Carregando PDFs...\n")

    documentos = ler_pdfs(PDF_PATH)

    if not documentos:
        print("Nenhum documento encontrado.")
        sys.exit(1)

    # CHUNKS
    print("\nCriando chunks...\n")

    chunks, metadados = preparar_documentos(documentos)

    print(f"Total de chunks: {len(chunks)}\n")

    # INDEXAÇÃO
    vetor_store = VetorStore(MODEL_NAME)

    vetor_store.adicionar_documentos(
        chunks,
        metadados
    )

    # LOOP PRINCIPAL
    while True:

        query = input("\nPergunta: ")

        if query.lower() == "sair":
            break

        # BUSCA NO RAG
        resultados = vetor_store.buscar(query)

        # GERA CONTEXTO
        contexto = gerar_contexto(resultados)
        print("\n================ Contexto ================\n")
        print(contexto)

        # CHAMA LLM
        resposta = agente.perguntar_llm(
            query,
            contexto
        )

        print("\n================ RESPOSTA ================\n")
        print(resposta)


if __name__ == "__main__":
    main()