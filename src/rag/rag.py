# =============================================================================
# rag_simples.py
# =============================================================================
# RAG simples com:
# - leitura de PDFs
# - chunking
# - embeddings
# - busca vetorial
# - retorno de contexto para LLM
#
# Pasta dos PDFs:
# D:\cod\jarvis-academico\data
#
# Instalação:
# pip install pypdf sentence-transformers faiss-cpu numpy
#
# Executar:
# python rag_simples.py
# =============================================================================

from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss


# =============================================================================
# LEITURA DOS PDFS
# =============================================================================

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


# =============================================================================
# CHUNKING
# =============================================================================

def criar_chunks(texto, chunk_size=500, overlap=100):
    chunks = []

    inicio = 0

    while inicio < len(texto):
        fim = inicio + chunk_size

        chunk = texto[inicio:fim]

        chunks.append(chunk)

        inicio += chunk_size - overlap

    return chunks


# =============================================================================
# PREPARAR DOCUMENTOS
# =============================================================================

def preparar_documentos(documentos):
    todos_chunks = []
    metadados = []

    for doc in documentos:
        chunks = criar_chunks(doc["texto"])

        for chunk in chunks:
            todos_chunks.append(chunk)

            metadados.append({
                "arquivo": doc["arquivo"]
            })

    return todos_chunks, metadados


# =============================================================================
# EMBEDDINGS
# =============================================================================

class VetorStore:

    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.metadados = []

    def adicionar_documentos(self, chunks, metadados):
        self.chunks = chunks
        self.metadados = metadados

        print("Gerando embeddings...")

        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True
        )

        embeddings = embeddings.astype("float32")

        dimensao = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimensao)

        self.index.add(embeddings)

        print(f"{len(chunks)} chunks indexados.")

    def buscar(self, pergunta, top_k=3):
        pergunta_embedding = self.model.encode(
            [pergunta],
            convert_to_numpy=True
        ).astype("float32")

        distancias, indices = self.index.search(
            pergunta_embedding,
            top_k
        )

        resultados = []

        for idx in indices[0]:
            resultados.append({
                "texto": self.chunks[idx],
                "arquivo": self.metadados[idx]["arquivo"]
            })

        return resultados


# =============================================================================
# GERAR CONTEXTO PARA LLM
# =============================================================================

def gerar_contexto(resultados):
    contexto = ""

    for i, item in enumerate(resultados, start=1):
        contexto += f"""
[DOCUMENTO {i}]
Arquivo: {item['arquivo']}

Conteúdo:
{item['texto']}

"""

    return contexto