import faiss
from sentence_transformers import SentenceTransformer


from src.utils.logger import configurar_logger

logger = configurar_logger()

class VetorStore:

    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.metadados = []

    def adicionar_documentos(self, chunks, metadados):
        self.chunks = chunks
        self.metadados = metadados

        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True,
            show_progress_bar=True
        ).astype("float32")

        faiss.normalize_L2(embeddings)

        dimensao = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimensao)
        self.index.add(embeddings)

        logger.info(f"{len(chunks)} chunks indexados.")

    def buscar(self, pergunta, top_k=8):
        pergunta_embedding = self.model.encode(
            [pergunta],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(pergunta_embedding)

        similaridades, indices = self.index.search(
            pergunta_embedding,
            top_k
        )

        resultados = []

        for score, idx in zip(similaridades[0], indices[0]):

            if idx == -1:
                continue

            resultados.append({
                "texto": self.chunks[idx],
                "arquivo": self.metadados[idx]["arquivo"],
                "chunk_index": self.metadados[idx]["chunk_index"],
                "total_chunks": self.metadados[idx]["total_chunks"],
                "similaridade": float(score),
            })

        return resultados