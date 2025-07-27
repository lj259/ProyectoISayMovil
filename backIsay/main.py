from fastapi import FastAPI, Depends
from typing import List
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@127.0.0.1/lanaapp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de la base de datos

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    tipo = Column(String(50))  # ingreso, egreso, ahorro
    usuario_id = Column(Integer)
    es_predeterminada = Column(Boolean)

class Transaccion(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    monto = Column(Float)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    tipo = Column(String(50))
    descripcion = Column(String(255))
    fecha = Column(Date)
    es_recurrente = Column(Boolean)
    id_recurrente = Column(Integer)
    fecha_creacion = Column(Date)

    categoria = relationship("Categoria", backref="transacciones")

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

#  Endpoint 1: Gráfico circular

class CategoriaTotal(BaseModel):
    categoria: str
    total: float

@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total por categoría según el tipo (ingreso, egreso, ahorro)
    """
    totales = defaultdict(float)

    transacciones = db.query(Transaccion).join(Categoria).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

# Endpoint 2: Gráfico de barras

class TendenciaMensual(BaseModel):
    mes: str
    total: float

@app.get("/graficas/tendencias", response_model=List[TendenciaMensual])
def tendencias_mensuales(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total mensual por tipo (ingreso, egreso, ahorro)
    """
    totales_por_mes = defaultdict(float)

    transacciones = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        if t.fecha:
            mes = t.fecha.month
            totales_por_mes[mes] += t.monto

    return [
        {"mes": MESES_ES[mes], "total": totales_por_mes[mes]}
        for mes in sorted(totales_por_mes.keys())
    ] 

# Endpoint 3: Resumen financiero

class ResumenFinanciero(BaseModel):
    total_ingresos: float
    total_egresos: float
    balance: float

@app.get("/resumen", response_model=ResumenFinanciero)
def resumen_financiero(usuario_id: int = 1, db: Session = Depends(get_db)):
    
    ingresos = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "ingreso"
    ).all()
    
    egresos = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "egreso"
    ).all()
    
    total_ingresos = sum(t.monto for t in ingresos)
    total_egresos = sum(t.monto for t in egresos)
    balance = total_ingresos - total_egresos

    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance
    } 

# Endpoint 4: Transacciones

# Modelo para la respuesta
class TransaccionOut(BaseModel):
    id: int
    monto: float
    tipo: str
    descripcion: str
    fecha: str
    categoria: str

    class Config:
        orm_mode = True

@app.get("/transacciones", response_model=List[TransaccionOut])
def listar_transacciones(usuario_id: int = 1, db: Session = Depends(get_db)):
    transacciones = db.query(Transaccion).join(Categoria).filter(
        Transaccion.usuario_id == usuario_id
    ).all()

    return [
        {
            "id": t.id,
            "monto": t.monto,
            "tipo": t.tipo,
            "descripcion": t.descripcion,
            "fecha": t.fecha.strftime("%Y-%m-%d"),
            "categoria": t.categoria.nombre if t.categoria else "Sin categoría"
        }
        for t in transacciones
    ]
