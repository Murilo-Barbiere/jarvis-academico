import os

PDF_PATH = os.getenv("PDF_PATH", "data")
DB_PATH = os.getenv("DB_PATH", "data/agenda.db")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

MODEL_NAME = "all-MiniLM-L6-v2"