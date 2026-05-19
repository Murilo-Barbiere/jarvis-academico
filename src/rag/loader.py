from pathlib import Path
from pypdf import PdfReader

def ler_pdfs(caminho):
    textos = []

    pasta = Path(caminho)

    pdfs = list(pasta.glob("*.pdf"))

    if not pdfs:
        print("Nenhum PDF encontrado.")
        return textos

    for pdf in pdfs:
        print(f"Lendo: {pdf.name}")

        try:
            reader = PdfReader(str(pdf))

            texto_pdf = ""

            for pagina in reader.pages:
                texto = pagina.extract_text()

                if texto:
                    texto_pdf += texto + "\n"

            textos.append({
                "arquivo": pdf.name,
                "texto": texto_pdf
            })

        except Exception as e:
            print(f"Erro ao ler {pdf.name}: {e}")

    return textos