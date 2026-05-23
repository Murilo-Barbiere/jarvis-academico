import logging
from pathlib import Path
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def ler_pdfs(caminho: str, incluir_subpastas: bool = False) -> list[dict]:
    pasta = Path(caminho)

    if not pasta.exists():
        logger.error(f"Pasta não encontrada: {caminho}")
        return []

    # rglob busca em subpastas; glob só na raiz
    padrao = "**/*.pdf" if incluir_subpastas else "*.pdf"
    pdfs = sorted(pasta.glob(padrao))

    if not pdfs:
        logger.warning(f"Nenhum PDF encontrado em: {caminho}")
        return []

    logger.info(f"Encontrados {len(pdfs)} PDF(s) em {caminho}")
    textos = []

    for pdf in pdfs:
        resultado = _ler_um_pdf(pdf)
        if resultado:
            textos.append(resultado)

    logger.info(f"{len(textos)}/{len(pdfs)} PDFs lidos com sucesso.")
    return textos


def _ler_um_pdf(caminho_pdf: Path) -> dict | None:
    try:
        logger.info(f"Lendo: {caminho_pdf.name}")
        reader = PdfReader(str(caminho_pdf))

        partes = []
        paginas_com_texto = 0

        for i, pagina in enumerate(reader.pages, start=1):
            texto = pagina.extract_text()

            if texto and texto.strip():
                # Marca o número de página para rastreabilidade
                partes.append(f"[Página {i}]\n{texto.strip()}")
                paginas_com_texto += 1

        # Detecta PDF escaneado: tem páginas mas nenhuma retornou texto
        if len(reader.pages) > 0 and paginas_com_texto == 0:
            logger.warning(
                f"{caminho_pdf.name} parece ser um PDF escaneado "
                f"(imagem sem texto extraível). OCR não implementado."
            )
            return None

        texto_completo = "\n\n".join(partes)

        logger.info(
            f"  ✓ {caminho_pdf.name}: "
            f"{paginas_com_texto}/{len(reader.pages)} páginas, "
            f"{len(texto_completo)} caracteres"
        )

        return {
            "arquivo": caminho_pdf.name,
            "texto": texto_completo,
            "paginas_lidas": paginas_com_texto,
        }

    except Exception as e:
        logger.error(f"Erro ao ler {caminho_pdf.name}: {e}")
        return None