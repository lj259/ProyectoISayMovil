from datetime import date
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# Configuración de la base de datos MySQL
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost/lanaapp"
# Ejemplo: "mysql+mysqlconnector://root:password@127.0.0.1/pagos_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modelo de la base de datos
class PagoFijo(Base):
    __tablename__ = "pagos_fijos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255), index=True)
    monto = Column(Float)
    fecha = Column(Date)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Modelo Pydantic para creación
class PagoFijoCreate(BaseModel):
    descripcion: str
    monto: float
    fecha: date

# Modelo Pydantic para respuesta
class PagoFijoResponse(PagoFijoCreate):
    id: int
    
    class Config:
        orm_mode = True

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return "API de Pagos Fijos con MySQL"

@app.post("/pagos-fijos/", response_model=PagoFijoResponse)
def create_pago_fijo(pago: PagoFijoCreate, db: Session = Depends(get_db)):
    db_pago = PagoFijo(**pago.dict())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.get("/pagos-fijos/", response_model=List[PagoFijoResponse])
def list_pagos_fijos(db: Session = Depends(get_db)):
    return db.query(PagoFijo).all()

@app.get("/pagos-fijos/{pago_id}", response_model=PagoFijoResponse)
def get_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    return db_pago

@app.put("/pagos-fijos/{pago_id}", response_model=PagoFijoResponse)
def update_pago_fijo(pago_id: int, pago: PagoFijoCreate, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    for key, value in pago.dict().items():
        setattr(db_pago, key, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.delete("/pagos-fijos/{pago_id}")
def delete_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    db.delete(db_pago)
    db.commit()
    return {"message": "Pago fijo eliminado correctamente"}