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