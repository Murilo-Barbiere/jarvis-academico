import json
import logging
from pathlib import Path
from rich.logging import RichHandler

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger("jarvis")

if not logger.handlers:
    # Nível base do logger (captura tudo para os handlers filtrarem)
    logger.setLevel(logging.DEBUG)

    # Formatter para Arquivo (Completo para debug)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    # Handler para Arquivo (Persiste tudo)
    file_handler = logging.FileHandler(
        LOG_FILE,
        mode="a",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler para Console (Compacto e limpo)
    console_handler = RichHandler(
        level=logging.INFO,
        rich_tracebacks=True,
        show_path=False,
        show_time=False,
        markup=True
    )
    logger.addHandler(console_handler)

    logger.propagate = False

def registrar_tool(nome_ferramenta, entrada, saida):
    """
    Registra os detalhes da tool de forma inteligente:
    - JSON completo vai para o arquivo de log (DEBUG)
    - Resumo amigável vai para o terminal (INFO)
    """
    log_data = {
        "tipo": "tool_call",
        "ferramenta": nome_ferramenta,
        "entrada": entrada,
        "saida": saida
    }
    
    # Gravamos o JSON pesado no log de arquivo (DEBUG)
    logger.debug(f"TOOL_DETAILS: {json.dumps(log_data, ensure_ascii=False)}")
    
    logger.info(f"Ferramenta utilizada: {nome_ferramenta}")

def configurar_logger():
    return logger
