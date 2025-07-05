from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union
from sqlalchemy import (
    create_engine, Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# Conexión a base de datos MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --- Modelos SQLAlchemy ---
class PresupuestoDB(Base):
    __tablename__ = "presupuestos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto = Column(DECIMAL(10, 2), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    fecha_creacion = Column(TIMESTAMP, default=datetime.now)
    fecha_actualizacion = Column(
        TIMESTAMP,
        default=datetime.now,
        onupdate=datetime.now
    )

class TransaccionDB(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto = Column(Float, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    tipo = Column(Enum('ingreso', 'gasto'), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha = Column(Date, nullable=False)
    es_recurrente = Column(Boolean, default=False)
    id_recurrente = Column(Integer, nullable=True)
    fecha_creacion = Column(
        TIMESTAMP,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )

# Crear tablas en la BD (si no existen)
Base.metadata.create_all(bind=engine)

# --- Modelos Pydantic ---
class Presupuesto(BaseModel):
    id: Optional[int] = None
    usuario_id: int
    categoria_id: int
    monto: float
    ano: int
    mes: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True

class Transaccion(BaseModel):
    id: Optional[int] = None
    usuario_id: int
    monto: float
    categoria_id: int
    tipo: str
    descripcion: Optional[str] = None
    fecha: date
    es_recurrente: Optional[bool] = False
    id_recurrente: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Inicialización de la app ---
app = FastAPI(title="LanaApp API")

# --- Rutas Presupuestos ---
@app.get("/presupuestos", response_model=List[Presupuesto], tags=["Presupuestos"])
def listar_presupuestos():
    db = SessionLocal()
    datos = db.query(PresupuestoDB).all()
    db.close()
    return datos

@app.get("/presupuestos/{id}", response_model=Presupuesto, tags=["Presupuestos"])
def obtener_presupuesto(id: int):
    db = SessionLocal()
    item = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return item

@app.post("/presupuestos", response_model=Presupuesto, tags=["Presupuestos"])
def crear_presupuesto(p: Presupuesto):
    db = SessionLocal()
    nuevo = PresupuestoDB(**p.dict(exclude_unset=True))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    db.close()
    return nuevo

@app.put("/presupuestos/{id}", response_model=Presupuesto, tags=["Presupuestos"])
def actualizar_presupuesto(id: int, datos: Presupuesto):
    db = SessionLocal()
    obj = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    if not obj:
        db.close()
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    db.close()
    return obj

@app.delete("/presupuestos/{id}", tags=["Presupuestos"])
def eliminar_presupuesto(id: int):
    db = SessionLocal()
    obj = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    if not obj:
        db.close()
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(obj)
    db.commit()
    db.close()
    return {"mensaje": "Presupuesto eliminado"}

# --- Rutas Transacciones ---
@app.get("/transacciones", response_model=List[Transaccion], tags=["Transacciones"])
def listar_transacciones():
    db = SessionLocal()
    ts = db.query(TransaccionDB).all()
    db.close()
    return ts

@app.get("/transacciones/{id}", response_model=Transaccion, tags=["Transacciones"])
def obtener_transaccion(id: int):
    db = SessionLocal()
    t = db.query(TransaccionDB).filter(TransaccionDB.id == id).first()
    db.close()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return t

@app.post("/transacciones", response_model=Transaccion, tags=["Transacciones"])
def agregar_transaccion(t: Transaccion):
    db = SessionLocal()
    nueva = TransaccionDB(**t.dict(exclude_unset=True, exclude={"id", "fecha_creacion"}))
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()
    return nueva

@app.put("/transacciones/{id}", response_model=Transaccion, tags=["Transacciones"])
def actualizar_transaccion(id: int, t: Transaccion):
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

@app.delete("/transacciones/{id}", tags=["Transacciones"])
def eliminar_transaccion(id: int):
    db = SessionLocal()
    trans = db.query(TransaccionDB).filter(TransaccionDB.id == id).first()
    if not trans:
        db.close()
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(trans)
    db.commit()
    db.close()
    return {"mensaje": "Transacción eliminada"}

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