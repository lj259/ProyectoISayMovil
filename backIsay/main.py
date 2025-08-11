# ——— Imports de terceros —————————————————————————————————————
from router import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
# SQLAlchemy ORM
from database import SessionLocal, Base
import uuid


# Inicialización de la app
app = FastAPI(title="LanaApp API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

