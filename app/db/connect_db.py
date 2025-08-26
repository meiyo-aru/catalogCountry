from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv  # Importa a função
from app.models.models import Base

load_dotenv() # carrega as variáveis de ambiente do arquivo .env
DATABASE_URL = str(os.getenv("DATABASE_URL")) # obtém a variável de ambiente

engine = create_engine(DATABASE_URL) # cria a conexão com o banco de dados
session = sessionmaker(autocommit=False, autoflush=False, bind=engine) # cria a sessão
Base.metadata.create_all(bind=engine) # cria as tabelas no banco de dados baseado nos modelos orm definidos

# função que entrega uma sessão de banco de dados
def get_db():
    db = session()
    try:
        yield db  # entrega o objeto para uso no endpoint
    finally:
        db.close()  # garante o fechamento da conexão após a resposta