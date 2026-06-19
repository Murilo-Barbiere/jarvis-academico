
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.text import Text

def main():
    console = Console()
    
    from src.utils.logger import configurar_logger
    logger = configurar_logger()
    logger.info("Aplicação JARVIS Acadêmico iniciada")

    from llm.Agente import get_agent
    from src.rag.VetorStore import VetorStore
    from src.config.setting import MODEL_NAME, PDF_PATH, VECTOR_STORE_PATH
    from src.rag.chunker import preparar_documentos
    from src.rag.loader import ler_pdfs
    from src.tools.tool_manager import executar_tool

    console.print(Panel(
        Text("JARVIS Acadêmico", style="bold blue", justify="center"),
        subtitle="Assistente Pessoal de Estudos",
        border_style="blue"
    ))

    with console.status("[bold green]Inicializando sistema...", spinner="dots"):
        jarvis = get_agent()
        vetor_store = VetorStore(MODEL_NAME)
        
        if not vetor_store.carregar(VECTOR_STORE_PATH):
            logger.info("Índice não encontrado ou inválido. Reconstruindo...")
            documentos = ler_pdfs(PDF_PATH)
            if not documentos:
                console.print("[yellow]Aviso: Nenhum documento PDF encontrado para o RAG.[/]")
                vetor_store = None
            else:
                chunks, metadados = preparar_documentos(documentos)
                vetor_store.adicionar_documentos(chunks, metadados)
                vetor_store.salvar(VECTOR_STORE_PATH)
                logger.info("Vector Store criada e salva com sucesso")
        else:
            logger.info(f"Índice carregado: {len(vetor_store.chunks)} chunks")

    console.print("[dim]Digite '/sair' para encerrar ou '/limpar' para resetar a memória.[/]")

    while True:
        if jarvis.modo_quiz:
            console.print("[bold yellow]>>> Modo quiz ativo <<<[/]")
            console.print("[dim]Digite '/sair quiz' para encerrar o modo quiz.[/]")

        query = Prompt.ask("\n[bold cyan]Você[/]")

        if query.lower() == "/sair":
            logger.info("Sistema encerrado pelo usuário")
            break
        
        if query.lower() == "/sair quiz":
            with console.status("[bold green]Encerrando quiz...", spinner="dots"):
                resposta = jarvis.encerrar_quiz(query)
            console.print(Panel(resposta, title="JARVIS", border_style="green"))
            continue

        if query.lower() == "/limpar":
            jarvis.memory.clear()
            console.print("[bold blue]Histórico de conversa limpo![/]")
            continue

        console.print() # Linha em branco para separar da pergunta
        with console.status("[bold green]Processando...", spinner="dots"):
            logger.debug(f"Query original: {query}")

            # 1. Agente decide o que fazer (Tool Calling com Histórico)
            plano = jarvis.decidir_tool(query)
            logger.debug(f"Plano de execução: {json.dumps(plano, ensure_ascii=False)}")
            
            lista_tools = plano.get("tools", [])
            resultados_acumulados = []
            
            tool_especial = "nenhuma"

            # 2. Execução Sequencial das Tools com Resiliência
            if lista_tools:
                for item in lista_tools:
                    nome_tool = item.get("tool")
                    argumentos = item.get("arguments", {})
                    
                    if nome_tool == "nenhuma" or not nome_tool:
                        continue
                    
                    try:
                        # Executa a tool
                        resultado = executar_tool(nome_tool, argumentos, vetor_store, historico=jarvis.memory.get_history())
                        resultados_acumulados.append({
                            "tool": nome_tool,
                            "status": "sucesso",
                            "resultado": resultado
                        })
                        logger.debug(f"Resultado da tool {nome_tool}: {resultado}")
                        
                        # Identifica tools que mudam o fluxo de resposta final
                        if nome_tool == "iniciar_quiz":
                            tool_especial = "iniciar_quiz"
                        elif nome_tool == "encerrar_quiz":
                            tool_especial = "encerrar_quiz"
                        elif nome_tool == "planejar_estudos" and tool_especial not in ["iniciar_quiz", "encerrar_quiz"]:
                            tool_especial = "planejar_estudos"

                    except Exception as e:
                        logger.error(f"Erro na execução da tool {nome_tool}: {e}")
                        resultados_acumulados.append({
                            "tool": nome_tool,
                            "status": "erro",
                            "mensagem": str(e)
                        })

                contexto = json.dumps(resultados_acumulados, ensure_ascii=False, default=str)
            else:
                contexto = "Nenhuma informação extra necessária além do histórico da conversa."

            # 3. Geração da Resposta Final (com síntese e atualização da memória)
            if tool_especial == "planejar_estudos":
                resposta = jarvis.gerar_plano_estudos(query, contexto)
            elif tool_especial == "iniciar_quiz":
                resposta = jarvis.iniciar_quiz(query, contexto)
            elif tool_especial == "encerrar_quiz":
                resposta = jarvis.encerrar_quiz()
            else:
                resposta = jarvis.gerar_resposta_final(query, contexto)
        
        console.print(Panel(resposta, title="JARVIS", border_style="blue"))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        console = Console()
        console.print(f"[bold red]CRITICAL ERROR:[/] {e}")
        traceback.print_exc()
