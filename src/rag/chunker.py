def criar_chunks(texto, chunk_size=500, overlap=100):
    chunks = []

    inicio = 0

    while inicio < len(texto):
        fim = inicio + chunk_size

        chunk = texto[inicio:fim]

        chunks.append(chunk)

        inicio += chunk_size - overlap

    return chunks

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