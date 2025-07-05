from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, Text,
    Enum, Boolean, ForeignKey, TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Conexión a base de datos MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --------------------------------------------------
# MODELO SQLALCHEMY
# --------------------------------------------------
class TransaccionDB(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto         = Column(Float, nullable=False)
    categoria_id  = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    tipo          = Column(Enum('ingreso','gasto'), nullable=False)
    descripcion   = Column(String(255), nullable=True)
    fecha         = Column(Date, nullable=False)
    es_recurrente = Column(Boolean, default=False)
    id_recurrente = Column(Integer, nullable=True)
    fecha_creacion = Column(
        TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP"
    )

# (Repite base.metadata.create_all si solo tengo esta tabla)
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# MODELO Pydantic
# --------------------------------------------------
class Transaccion(BaseModel):
    id: Optional[int]
    usuario_id: int
    monto: float
    categoria_id: int
    tipo: str
    descripcion: Optional[str]
    fecha: date
    es_recurrente: Optional[bool] = False
    id_recurrente: Optional[int]
    fecha_creacion: Optional[datetime]

    class Config:
        orm_mode = True

# --------------------------------------------------
# RUTAS
# --------------------------------------------------
@app.get("/")
def read_root():
    return {"mensaje": "API de transacciones"}

@app.get("/transacciones", response_model=List[Transaccion])
def get_transacciones():
    db = SessionLocal()
    ts = db.query(TransaccionDB).all()
    db.close()
    return ts

@app.get("/transacciones/{id}", response_model=Transaccion)
def get_transaccion(id: int):
    db = SessionLocal()
    t = db.query(TransaccionDB).filter(TransaccionDB.id == id).first()
    db.close()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return t

@app.post("/transacciones", response_model=Transaccion)
def create_transaccion(t: Transaccion):
    db = SessionLocal()
    nueva = TransaccionDB(**t.dict(exclude_unset=True, exclude={"id","fecha_creacion"}))
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()
    return nueva

@app.put("/transacciones/{id}", response_model=Transaccion)
def update_transaccion(id: int, t: Transaccion):
    db = SessionLocal()
    trans = db.query(TransaccionDB).filter(TransaccionDB.id == id).first()
    if not trans:
        db.close()
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    for key, value in t.dict(exclude_unset=True, exclude={"fecha_creacion"}).items():
        setattr(trans, key, value)
    db.commit()
    db.refresh(trans)
    db.close()
    return trans

@app.delete("/transacciones/{id}")
def delete_transaccion(id: int):
    db = SessionLocal()
    trans = db.query(TransaccionDB).filter(TransaccionDB.id == id).first()
    if not trans:
        db.close()
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(trans)
    db.commit()
    db.close()
    return {"mensaje": "Transacción eliminada"}
