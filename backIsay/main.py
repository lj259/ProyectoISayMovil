from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship


SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@127.0.0.1/lanaapp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    tipo = Column(String(50))  
    usuario_id = Column(Integer, default=1)
    es_predeterminada = Column(Boolean, default=False)

class Transaccion(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    monto = Column(Float)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    tipo = Column(String(50)) 
    descripcion = Column(String(255))
    fecha = Column(Date)
    es_recurrente = Column(Boolean, default=False)
    id_recurrente = Column(Integer, nullable=True)
    fecha_creacion = Column(Date)

    categoria = relationship("Categoria", backref="transacciones")


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


class CategoriaTotal(BaseModel):
    categoria: str
    total: float

class TendenciaMensual(BaseModel):
    mes: str
    total: float

class ResumenFinanciero(BaseModel):
    total_ingresos: float
    total_egresos: float
    total_ahorros: float
    balance: float

class TransaccionOut(BaseModel):
    id: int
    monto: float
    tipo: str
    descripcion: str
    fecha: str
    categoria: Optional[str]

    class Config:
        orm_mode = True

class TransaccionCreate(BaseModel):
    monto: float
    categoria: str         
    tipo: Optional[str] = None  
    descripcion: str
    fecha: str            # YYYY-MM-DD


# Endpoints de categorías

@app.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """
    Devuelve todas las categorías (id, nombre, tipo, usuario_id, es_predeterminada).
    """
    cats = db.query(Categoria).all()
    return [
        {
            "id": c.id,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "usuario_id": c.usuario_id,
            "es_predeterminada": bool(c.es_predeterminada)
        } for c in cats
    ]

@app.post("/categorias/init")
def inicializar_categorias(db: Session = Depends(get_db)):
    """
    Inserta las 5 categorías por defecto si no existen.
    Úsalo una vez después de desplegar o para pruebas.
    """
    defaults = [
        ("Comida", "egreso"),
        ("Transporte", "egreso"),
        ("Servicios", "egreso"),
        ("Entretenimiento", "egreso"),
        ("Salario", "ingreso"),
    ]
    creadas = []
    for nombre, tipo in defaults:
        existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
        if not existe:
            c = Categoria(nombre=nombre, tipo=tipo, usuario_id=1, es_predeterminada=True)
            db.add(c)
            creadas.append(nombre)
    db.commit()
    return {"insertadas": creadas, "mensaje": "Inicialización completada (si faltaban categorías)."}

# Endpoint 1: Gráfico circular (por categoría)

@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total por categoría según el tipo (ingreso, egreso, ahorro).
    Si una transacción no tiene categoría, suma por su tipo.
    """
    totales = defaultdict(float)

    transacciones = db.query(Transaccion).join(Categoria, isouter=True).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto
        else:
            totales[t.tipo.capitalize()] += t.monto

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

# Endpoint 2: Gráfico de barras (tendencias)

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

    ahorros = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "ahorro"
    ).all()

    total_ingresos = sum(t.monto for t in ingresos)
    total_egresos = sum(t.monto for t in egresos)
    total_ahorros = sum(t.monto for t in ahorros)
    balance = total_ingresos - total_egresos + total_ahorros

    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "total_ahorros": total_ahorros,
        "balance": balance
    }


# Endpoint 4: Transacciones 

@app.get("/transacciones", response_model=List[TransaccionOut])
def listar_transacciones(usuario_id: int = 1, db: Session = Depends(get_db)):
    transacciones = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id
    ).all()

    return [
        {
            "id": t.id,
            "monto": t.monto,
            "tipo": t.tipo,
            "descripcion": t.descripcion,
            "fecha": t.fecha.strftime("%Y-%m-%d") if t.fecha else "",
            "categoria": t.categoria.nombre if t.categoria else t.tipo.capitalize()
        }
        for t in transacciones
    ]

# Crear transacción

@app.post("/transacciones")
def crear_transaccion(data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    
    categoria_obj = db.query(Categoria).filter(Categoria.nombre == data.categoria).first()
    if not categoria_obj:
        raise HTTPException(status_code=400, detail=f"Categoría '{data.categoria}' no es válida.")

    
    tipo_final = None
    if data.tipo:
        tipo_final = data.tipo.lower()
        if categoria_obj.tipo and categoria_obj.tipo.lower() != tipo_final:
            raise HTTPException(status_code=400, detail=f"El tipo proporcionado '{data.tipo}' no coincide con el tipo de la categoría ('{categoria_obj.tipo}').")
    else:
        tipo_final = categoria_obj.tipo.lower() if categoria_obj.tipo else None
        if not tipo_final:
            raise HTTPException(status_code=400, detail="No se pudo determinar el 'tipo' (ingreso/egreso). Proporciona 'tipo' en el payload o configura 'tipo' en la categoría.")

    nueva_transaccion = Transaccion(
        usuario_id=usuario_id,
        monto=data.monto,
        tipo=tipo_final,
        descripcion=data.descripcion,
        fecha=datetime.strptime(data.fecha, "%Y-%m-%d").date(),
        categoria_id=categoria_obj.id,
        fecha_creacion=datetime.now().date(),
        es_recurrente=False,
        id_recurrente=None
    )
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    return {"mensaje": "Transacción creada correctamente", "id": nueva_transaccion.id}

# Editar transacción

@app.put("/transacciones/{id}")
def editar_transaccion(id: int, data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == id, Transaccion.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    categoria_obj = db.query(Categoria).filter(Categoria.nombre == data.categoria).first()
    if not categoria_obj:
        raise HTTPException(status_code=400, detail=f"Categoría '{data.categoria}' no es válida.")

    # Determinar tipo final
    if data.tipo:
        tipo_final = data.tipo.lower()
        if categoria_obj.tipo and categoria_obj.tipo.lower() != tipo_final:
            raise HTTPException(status_code=400, detail=f"El tipo proporcionado '{data.tipo}' no coincide con el tipo de la categoría ('{categoria_obj.tipo}').")
    else:
        tipo_final = categoria_obj.tipo.lower() if categoria_obj.tipo else None
        if not tipo_final:
            raise HTTPException(status_code=400, detail="No se pudo determinar el 'tipo' (ingreso/egreso). Proporciona 'tipo' en el payload o configura 'tipo' en la categoría.")

    transaccion.monto = data.monto
    transaccion.tipo = tipo_final
    transaccion.descripcion = data.descripcion
    transaccion.fecha = datetime.strptime(data.fecha, "%Y-%m-%d").date()
    transaccion.categoria_id = categoria_obj.id

    db.commit()
    db.refresh(transaccion)
    return {"mensaje": "Transacción actualizada correctamente"}

# Eliminar transacción

@app.delete("/transacciones/{id}")
def eliminar_transaccion(id: int, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == id, Transaccion.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}