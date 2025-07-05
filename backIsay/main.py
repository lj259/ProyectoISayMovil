from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, Float, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuración conexión MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Modelo BD
class PresupuestoDB(Base):
    __tablename__ = "presupuestos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    monto = Column(DECIMAL(10, 2), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    fecha_creacion = Column(TIMESTAMP, default=datetime.now)
    fecha_actualizacion = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

# Modelo de entrada/salida
class Presupuesto(BaseModel):
    id: int | None = None
    usuario_id: int
    categoria_id: int
    monto: float
    ano: int
    mes: int

    class Config:
        orm_mode = True


# --- Inicialización de la app ---
app = FastAPI(title="LanaApp")


# GET /presupuestos
@app.get("/presupuestos", response_model=List[Presupuesto], tags=["Presupuestos"])
def listar_presupuestos():
    db = Session()
    datos = db.query(PresupuestoDB).all()
    db.close()
    return datos

# GET /presupuestos/{id}
@app.get("/presupuestos/{id}", response_model=Presupuesto, tags=["Presupuestos"])
def obtener_presupuesto(id: int):
    db = Session()
    item = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return item

# POST /presupuestos
@app.post("/presupuestos", response_model=Presupuesto, tags=["Presupuestos"])
def crear_presupuesto(p: Presupuesto):
    db = Session()
    nuevo = PresupuestoDB(**p.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    db.close()
    return nuevo

# PUT /presupuestos/{id}
@app.put("/presupuestos/{id}", response_model=Presupuesto, tags=["Presupuestos"])
def actualizar_presupuesto(id: int, datos: Presupuesto):
    db = Session()
    obj = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    if not obj:
        db.close()
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    for key, value in datos.dict().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    db.close()
    return obj

# DELETE /presupuestos/{id}
@app.delete("/presupuestos/{id}", tags=["Presupuestos"])
def eliminar_presupuesto(id: int):
    db = Session()
    obj = db.query(PresupuestoDB).filter(PresupuestoDB.id == id).first()
    if not obj:
        db.close()
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(obj)
    db.commit()
    db.close()
    return {"mensaje": "Presupuesto eliminado"}
