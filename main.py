import sys

from src.rag.chunker import preparar_documentos
from src.rag.context_builder import gerar_contexto
from src.rag.loader import ler_pdfs

from src.llm import GammaAgente as agente
from src.config.setting import MODEL_NAME, PDF_PATH
from src.rag.VetorStore import VetorStore
from src.utils.logger import configurar_logger
from src.tools.tool_manager import executar_tool


def main():

    logger = configurar_logger()

    logger.info("Aplicação iniciada")

    documentos = ler_pdfs(PDF_PATH)

    if not documentos:

        print("Nenhum documento encontrado.")

        logger.error("Nenhum documento encontrado no dataset")

        sys.exit(1)

    chunks, metadados = preparar_documentos(documentos)

    vetor_store = VetorStore(MODEL_NAME)

    vetor_store.adicionar_documentos(chunks, metadados)

    logger.info("Vector Store criada com sucesso")

    while True:

        query = input("\nPergunta: ")

        if query.lower() == "sair":

            logger.info("Sistema encerrado")

            break

        logger.info(f"Query recebida: {query}")

        # -----------------------------
        # LLM decide se precisa tool
        # -----------------------------
        tool_call = agente.decidir_tool(query)

        # -----------------------------
        # CASO TENHA TOOL
        # -----------------------------
        if tool_call and "tool" in tool_call:

            nome_tool = tool_call["tool"]

            argumentos = tool_call.get("arguments", {})

            logger.info(f"Tool escolhida: {nome_tool}")

            logger.info(f"Argumentos: {argumentos}")

            try:

                resultado_tool = executar_tool(
                    nome_tool,
                    argumentos,
                    vetor_store
                )

                logger.info("Tool executada com sucesso")

                if isinstance(resultado_tool, list) and len(resultado_tool) == 0:
                    contexto = "A ferramenta nao retornou resultados. Informe isso ao usuario claramente."
                else:
                    contexto = str(resultado_tool)

            except Exception as e:

                logger.error(f"Erro ao executar tool: {str(e)}")

                contexto = f"Erro ao executar ferramenta: {str(e)}"

        # -----------------------------
        # CASO NÃO TENHA TOOL
        # -----------------------------
        else:

            logger.info("Nenhuma tool utilizada")

            resultados = vetor_store.buscar(query)

            logger.info(f"Chunks recuperados: {len(resultados)}")

            for i, item in enumerate(resultados, start=1):

                logger.info(
                    f"[Chunk {i}] arquivo={item['arquivo']}"
                )

            contexto = gerar_contexto(resultados)

        # -----------------------------
        # DEBUG CONTEXTO
        # -----------------------------
        print("\n\n--------------------CONTEXTO--------------------")
        print(contexto)
        print("--------------------CONTEXTO--------------------")

        # -----------------------------
        # RESPOSTA FINAL DA LLM
        # -----------------------------
        resposta = agente.perguntar_llm(
            mensagem=query,
            contexto=contexto
        )

        logger.info(
            f"Resposta gerada | tamanho={len(resposta)}"
        )

        print("\n\n--------------------RESPOSTA--------------------")
        print(resposta)


if __name__ == "__main__":
    main()