# Instalação:
# pip install pypdf sentence-transformers faiss-cpu numpy

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss


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