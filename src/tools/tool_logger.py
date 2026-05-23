from datetime import datetime
import json
import os

LOG_PATH = "logs/tools.log"

def registrar_log(nome_ferramenta, entrada, saida):

    os.makedirs("logs", exist_ok=True)

    log = {
        "timestamp": datetime.now().isoformat(),
        "ferramenta": nome_ferramenta,
        "entrada": entrada,
        "saida": saida
    }

    with open(LOG_PATH, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(log, ensure_ascii=False) + "\n")