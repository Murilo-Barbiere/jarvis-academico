import logging

logger = logging.getLogger()

def gerar_contexto(resultados: list[dict], max_chars: int = 3000,) -> str:
    if not resultados:
        return "Nenhum trecho relevante encontrado nos documentos."

    vistos = set()
    unicos = []

    for r in resultados:
        chave = r["texto"][:80].strip()
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(r)

    if len(unicos) < len(resultados):
        logger.debug(f"Deduplicação: {len(resultados)} → {len(unicos)} chunks únicos")

    partes = []
    chars_acumulados = 0

    for i, item in enumerate(unicos, start=1):
        score = item.get("similaridade", 0)
        chunk_info = item.get("chunk_index")
        info_chunk = f" | parte {chunk_info + 1}" if chunk_info is not None else ""

        trecho = (
            f"[Trecho {i} — {item['arquivo']}{info_chunk} | "
            f"relevância: {score:.0%}]\n"
            f"{item['texto']}\n"
        )

        if chars_acumulados + len(trecho) > max_chars:
            logger.debug(f"Limite de {max_chars} chars atingido em {i - 1} trechos.")
            break

        partes.append(trecho)
        chars_acumulados += len(trecho)

    if not partes:
        return "Contexto muito longo para processar. Tente uma pergunta mais específica."

    contexto = "\n---\n".join(partes)

    logger.debug(f"Contexto gerado: {len(contexto)} chars, {len(partes)} trechos")
    return contexto