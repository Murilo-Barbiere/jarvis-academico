import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


logger = logging.getLogger("jarvis")

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    # Handler para Arquivo
    file_handler = logging.FileHandler(
        LOG_FILE,
        mode="a",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para Console (Terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.propagate = False

def registrar_tool(nome_ferramenta, entrada, saida):

    logger.info(
        json.dumps(
            {
                "tipo": "tool_call",
                "ferramenta": nome_ferramenta,
                "entrada": entrada,
                "saida": saida
            },
            ensure_ascii=False
        )
    )

def configurar_logger():
    return logger
