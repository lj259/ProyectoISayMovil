from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ Cambia estos datos por los reales de tu base de datos MySQL
USER = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "3306"
DB_NAME = "lanaapp"

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# Crear conexión con la base de datos MySQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
