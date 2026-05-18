from sqlalchemy import engine

import llm.GammaAgente as GammaAgente 
from database.models import Base

Base.metadata.create_all(bind=engine)
print("Banco criado.")

query = input("pergunta pra llm: ")

resposta = GammaAgente.perguntar_llm(query)
print(resposta) 