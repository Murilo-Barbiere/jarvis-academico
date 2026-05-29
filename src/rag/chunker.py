from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

from src.utils.logger import configurar_logger

logger = configurar_logger()


def limpar_texto(texto: str) -> str:
    texto = re.sub(r"-\n(\w)", r"\1", texto)
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)
    texto = re.sub(r"\n{2,}", "\n\n", texto)
    texto = re.sub(r"\s+", " ", texto)

    substituicoes = {
        "¢": "é",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "’": "'",
        "“": '"',
        "”": '"',
    }

    for errado, correto in substituicoes.items():
        texto = texto.replace(errado, correto)

    return texto.strip()


def criar_chunks(texto, chunk_size=1000, overlap=200):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )

    return splitter.split_text(texto)


def preparar_documentos(documentos):
    todos_chunks = []
    metadados = []

    logger.info(f"Preparando documentos: {len(documentos)}")

    for doc in documentos:

        texto_limpo = limpar_texto(doc["texto"])

        chunks = criar_chunks(texto_limpo)

        total_chunks = len(chunks)

        logger.info(
            f"Documento: {doc['arquivo']} | "
            f"chunks={total_chunks}"
        )

        for i, chunk in enumerate(chunks):

            todos_chunks.append(chunk)

            metadados.append({
                "arquivo": doc["arquivo"],
                "chunk_index": i,
                "total_chunks": total_chunks,
            })

    logger.info(f"Total final de chunks: {len(todos_chunks)}")

    return todos_chunks, metadados