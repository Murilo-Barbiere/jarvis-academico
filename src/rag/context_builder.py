from difflib import SequenceMatcher
from src.utils.logger import configurar_logger

logger = configurar_logger()


def parecido(a, b, limite=0.90):
    return SequenceMatcher(None, a, b).ratio() > limite


def deduplicar_chunks(resultados):

    unicos = []

    for r in resultados:
        duplicado = False

        for u in unicos:
            if parecido(r["texto"], u["texto"]):
                duplicado = True
                break

        if not duplicado:
            unicos.append(r)

    return unicos


def gerar_contexto(
    resultados: list[dict],
    max_chars: int = 5000,
) -> str:

    if not resultados:
        return "Nenhum trecho relevante encontrado nos documentos."

    unicos = deduplicar_chunks(resultados)

    if len(unicos) < len(resultados):
        logger.debug(
            f"Deduplicação: "
            f"{len(resultados)} → {len(unicos)} chunks únicos"
        )

    unicos.sort(
        key=lambda x: x.get("similaridade", 0),
        reverse=True
    )

    partes = []

    chars_acumulados = 0

    for i, item in enumerate(unicos, start=1):

        score = item.get("similaridade", 0)

        chunk_index = item.get("chunk_index", 0)
        total_chunks = item.get("total_chunks", 0)

        trecho = (
            f"[Documento: {item['arquivo']}]\n"
            f"[Parte {chunk_index + 1}/{total_chunks}]\n"
            f"[Relevância: {score:.1%}]\n\n"
            f"{item['texto']}\n"
        )

        if chars_acumulados + len(trecho) > max_chars:

            logger.debug(
                f"Limite de {max_chars} chars "
                f"atingido em {i - 1} trechos."
            )

            break

        partes.append(trecho)

        chars_acumulados += len(trecho)

    if not partes:
        return (
            "Contexto muito longo para processar. "
            "Tente uma pergunta mais específica."
        )

    contexto = "\n\n---\n\n".join(partes)

    logger.debug(
        f"Contexto gerado: "
        f"{len(contexto)} chars, "
        f"{len(partes)} trechos"
    )

    documentos_final = sorted(list(set(item['arquivo'] for item in unicos[:len(partes)])))
    logger.info(f"Documentos usados para gerar o contexto final: {documentos_final}")

    return contexto