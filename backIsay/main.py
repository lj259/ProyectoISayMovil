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
from passlib.context import CryptContext

DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    esta_activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP)
    fecha_actualizacion = Column(TIMESTAMP)

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    tipo = Column(Enum('ingreso', 'gasto'), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    es_predeterminada = Column(Boolean, default=False)

class Presupuesto(Base):
    __tablename__ = "presupuestos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto = Column(DECIMAL(10, 2), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    fecha_creacion = Column(TIMESTAMP, default=datetime.now)
    fecha_actualizacion = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

class Transaccion(Base):
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
    fecha_creacion = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")

class PagoFijo(Base):
    __tablename__ = "pagos_fijos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    descripcion = Column(String(255), index=True)
    monto = Column(Float)
    fecha = Column(Date)

Base.metadata.create_all(bind=engine)

class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: str
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contraseña: str

class Usuario(UsuarioBase):
    id: int
    esta_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    correo: str
    contraseña: str

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
    
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="LanaApp API", version="1.0.0")

# --- Autenticación ---
@app.post("/register", response_model=Usuario,tags=["Usuarios"])
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    user_in_db = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = pwd_context.hash(user.contraseña)
    nuevo_usuario = Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña=hashed_password,
        telefono=user.telefono,
        esta_activo=True
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/login",tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if not usuario or not pwd_context.verify(user.contraseña, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario.nombre_usuario,
        "usuario_id": usuario.id
    }

# --- Rutas Presupuestos ---
@app.get("/presupuestos", response_model=List[Presupuesto], tags=["Presupuestos"])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(Presupuesto).all()

@app.get("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return presupuesto

@app.post("/presupuestos", response_model=Presupuesto, tags=["Presupuestos"])
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = Presupuesto(**presupuesto.dict())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@app.put("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def actualizar_presupuesto(presupuesto_id: int, presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    for key, value in presupuesto.dict().items():
        setattr(db_presupuesto, key, value)
    
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@app.delete("/presupuestos/{presupuesto_id}", tags=["Presupuestos"])
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    db.delete(db_presupuesto)
    db.commit()
    return {"mensaje": "Presupuesto eliminado correctamente"}

# --- Rutas Transacciones ---
@app.get("/transacciones", response_model=List[Transaccion], tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(Transaccion).all()

@app.get("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@app.post("/transacciones", response_model=Transaccion, tags=["Transacciones"])
def agregar_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = Transaccion(**transaccion.dict())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.put("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def actualizar_transaccion(transaccion_id: int, transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    for key, value in transaccion.dict().items():
        setattr(db_transaccion, key, value)
    
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@app.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    db.delete(db_transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}

# --- Rutas Pagos Fijos ---
@app.get("/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(PagoFijo)
    if usuario_id:
        query = query.filter(PagoFijo.usuario_id == usuario_id)
    return query.all()

@app.get("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def obtener_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    return pago

@app.post("/pagos-fijos", response_model=PagoFijo, tags=["Pagos Fijos"])
def crear_pago_fijo(pago: PagoFijoCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    existe_pago = db.query(PagoFijo).filter(
        PagoFijo.descripcion == pago.descripcion,
        PagoFijo.usuario_id == pago.usuario_id,
        PagoFijo.monto == pago.monto
    ).first()
    
    if existe_pago:
        raise HTTPException(status_code=400, detail="Ya existe un pago fijo similar para este usuario")
    
    db_pago = PagoFijo(**pago.dict())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.put("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def actualizar_pago_fijo(pago_id: int, pago: PagoFijoCreate, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for key, value in pago.dict().items():
        setattr(db_pago, key, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago

@app.delete("/pagos-fijos/{pago_id}", tags=["Pagos Fijos"])
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    db.delete(db_pago)
    db.commit()
    return {"mensaje": "Pago fijo eliminado correctamente"}

@app.get("/usuarios/{usuario_id}/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return db.query(PagoFijo).filter(PagoFijo.usuario_id == usuario_id).all()

@app.get("/")
def home():
    return {"message": "Bienvenido a la API de LanaApp"}