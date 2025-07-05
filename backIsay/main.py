from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, datetime


DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)

class CategoriaDB(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    
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

class PagoFijoDB(Base):
    __tablename__ = "pagos_fijos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    descripcion = Column(String(255), index=True)
    monto = Column(Float)
    fecha = Column(Date)
# Crear tablas en la BD (si no existen)
Base.metadata.create_all(bind=engine)

# --- Modelos Pydantic ---
class PresupuestoBase(BaseModel):
    usuario_id: int
    categoria_id: int
    monto: float
    ano: int
    mes: int

class PresupuestoCreate(PresupuestoBase):
    pass

class Presupuesto(PresupuestoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True

class TransaccionBase(BaseModel):
    usuario_id: int
    monto: float
    categoria_id: int
    tipo: str
    fecha: date
    descripcion: Optional[str] = None
    es_recurrente: Optional[bool] = False
    id_recurrente: Optional[int] = None

class TransaccionCreate(TransaccionBase):
    pass

class Transaccion(TransaccionBase):
    id: int
    fecha_creacion: datetime

    class Config:
        orm_mode = True
        
class PagoFijoBase(BaseModel):
    descripcion: str
    monto: float
    fecha: date
    usuario_id: int 

class PagoFijoCreate(PagoFijoBase):
    pass

class PagoFijo(PagoFijoBase):
    id: int
    
    class Config: # Configuración para Pydantic
        orm_mode = True


def get_db(): # dependencia para obtener la sesión de la base de datos
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="LanaApp API", version="1.0.0")

# --- Rutas Presupuestos ---
@app.get("/presupuestos", response_model=List[Presupuesto], tags=["Presupuestos"])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(PresupuestoDB).all()

@app.get("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    presupuesto = db.query(PresupuestoDB).filter(PresupuestoDB.id == presupuesto_id).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return presupuesto

@app.post("/presupuestos", response_model=Presupuesto, tags=["Presupuestos"])
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = PresupuestoDB(**presupuesto.dict())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@app.put("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def actualizar_presupuesto(presupuesto_id: int, presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = db.query(PresupuestoDB).filter(PresupuestoDB.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    for key, value in presupuesto.dict().items():
        setattr(db_presupuesto, key, value)
    
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@app.delete("/presupuestos/{presupuesto_id}", tags=["Presupuestos"])
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = db.query(PresupuestoDB).filter(PresupuestoDB.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    db.delete(db_presupuesto)
    db.commit()
    return {"mensaje": "Presupuesto eliminado correctamente"}

# --- Rutas Transacciones ---
@app.get("/transacciones", response_model=List[Transaccion], tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(TransaccionDB).all()

@app.get("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == transaccion_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@app.post("/transacciones", response_model=Transaccion, tags=["Transacciones"])
def agregar_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = TransaccionDB(**transaccion.dict())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.put("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def actualizar_transaccion(transaccion_id: int, transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    for key, value in transaccion.dict().items():
        setattr(db_transaccion, key, value)
    
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    db.delete(db_transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}

# --- Rutas Pagos Fijos ---
@app.get("/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos(
    usuario_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(PagoFijoDB)
    if usuario_id is not None:
        query = query.filter(PagoFijoDB.usuario_id == usuario_id)
    return query.all()

@app.get("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def obtener_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(PagoFijoDB).filter(PagoFijoDB.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    if pago.usuario_id:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == pago.usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuario asociado al pago fijo no encontrado"
            )
    
    return pago

@app.post("/pagos-fijos", response_model=PagoFijo, tags=["Pagos Fijos"])
def crear_pago_fijo(pago: PagoFijoCreate, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    existe_pago = db.query(PagoFijoDB).filter(
        PagoFijoDB.descripcion == pago.descripcion,
        PagoFijoDB.usuario_id == pago.usuario_id,
        PagoFijoDB.monto == pago.monto
    ).first()
    
    if existe_pago:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un pago fijo similar para este usuario"
        )
    
    db_pago = PagoFijoDB(**pago.dict())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.put("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def actualizar_pago_fijo(
    pago_id: int, 
    pago: PagoFijoCreate, 
    db: Session = Depends(get_db)
):

    db_pago = db.query(PagoFijoDB).filter(PagoFijoDB.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for key, value in pago.dict().items():
        setattr(db_pago, key, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.delete("/pagos-fijos/{pago_id}", tags=["Pagos Fijos"])
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijoDB).filter(PagoFijoDB.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    db.delete(db_pago)
    db.commit()
    return {"mensaje": "Pago fijo eliminado correctamente"}

@app.get("/usuarios/{usuario_id}/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return db.query(PagoFijoDB).filter(PagoFijoDB.usuario_id == usuario_id).all()
@app.get("/")
def home():
    return {"message": "Bienvenido a la API de LanaApp"}