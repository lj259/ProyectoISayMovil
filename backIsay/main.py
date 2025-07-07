# contraseña y recuperación de contraseña
import uuid
from datetime import date, datetime, timedelta
from collections import defaultdict
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine, Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

# Función simulada de envío de email
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")

# --- Configuración de la base de datos ---
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Modelos SQLAlchemy (DB) ---
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id                  = Column(Integer, primary_key=True, index=True)
    nombre_usuario      = Column(String(50), unique=True, nullable=False)
    correo              = Column(String(100), unique=True, nullable=False)
    contraseña_hash     = Column(String(255), nullable=False)
    telefono            = Column(String(20), nullable=True)
    esta_activo         = Column(Boolean, default=True)
    fecha_creacion      = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

class CategoriaDB(Base):
    __tablename__ = "categorias"
    id                = Column(Integer, primary_key=True, index=True)
    nombre            = Column(String(50), nullable=False)
    tipo              = Column(Enum('ingreso', 'gasto'), nullable=False)
    usuario_id        = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    es_predeterminada = Column(Boolean, default=False)

class PresupuestoDB(Base):
    __tablename__ = "presupuestos"
    id                  = Column(Integer, primary_key=True, index=True)
    usuario_id          = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id        = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto               = Column(DECIMAL(10, 2), nullable=False)
    ano                 = Column(Integer, nullable=False)
    mes                 = Column(Integer, nullable=False)
    fecha_creacion      = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

class TransaccionDB(Base):
    __tablename__ = "transacciones"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id     = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto          = Column(Float, nullable=False)
    categoria_id   = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    tipo           = Column(Enum('ingreso','gasto'), nullable=False)
    descripcion    = Column(String(255), nullable=True)
    fecha          = Column(Date, nullable=False)
    es_recurrente  = Column(Boolean, default=False)
    id_recurrente  = Column(Integer, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class PagoFijoDB(Base):
    __tablename__ = "pagos_fijos"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id     = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    descripcion    = Column(String(255), nullable=False)
    monto          = Column(Float, nullable=False)
    fecha          = Column(Date, nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class PasswordResetDB(Base):
    __tablename__ = "password_resets"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    token      = Column(String(100), unique=True, index=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# --- Schemas Pydantic ---
class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: str
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contraseña: str

class UsuarioRead(UsuarioBase):
    id: int
    esta_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    correo: str
    contraseña: str

class PasswordRecoveryRequest(BaseModel):
    correo: str

class PasswordResetRequest(BaseModel):
    nueva_contraseña: str = Field(..., min_length=6)

class PresupuestoBase(BaseModel):
    usuario_id: int
    categoria_id: int
    monto: float
    ano: int
    mes: int

class PresupuestoCreate(PresupuestoBase): pass

class PresupuestoRead(PresupuestoBase):
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

class TransaccionCreate(TransaccionBase): pass

class TransaccionRead(TransaccionBase):
    id: int
    fecha_creacion: datetime
    class Config:
        orm_mode = True

class PagoFijoBase(BaseModel):
    usuario_id: int
    descripcion: str
    monto: float
    fecha: date

class PagoFijoCreate(PagoFijoBase): pass

class PagoFijoRead(PagoFijoBase):
    id: int
    fecha_creacion: datetime
    class Config:
        orm_mode = True

class CategoriaTotal(BaseModel):
    categoria: str
    total: float

class TendenciaMensual(BaseModel):
    mes: str
    total: float

class ResumenFinanciero(BaseModel):
    total_ingresos: float
    total_egresos: float
    balance: float

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicialización de la app
app = FastAPI(title="LanaApp API", version="1.0.0")


# --- Endpoints Usuarios ---
from typing import List
from fastapi import HTTPException, Depends, BackgroundTasks
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register", response_model=UsuarioRead, tags=["Usuarios"])
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(UsuarioDB).filter(UsuarioDB.correo == user.correo).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    hashed = pwd_context.hash(user.contraseña)
    nuevo = UsuarioDB(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña_hash=hashed,
        telefono=user.telefono
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.post("/login", tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    u = db.query(UsuarioDB).filter(UsuarioDB.correo == user.correo).first()
    if not u or not pwd_context.verify(user.contraseña, u.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": u.nombre_usuario,
        "usuario_id": u.id
    }

@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(UsuarioDB).all()

@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    u = db.query(UsuarioDB).get(usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@app.post("/password-recovery", tags=["Usuarios"])
def password_recovery(
    req: PasswordRecoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    u = db.query(UsuarioDB).filter(UsuarioDB.correo == req.correo).first()
    mensaje = {"mensaje": "Si el correo existe, recibirás instrucciones por email."}
    if not u:
        return mensaje
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=1)
    pr = PasswordResetDB(user_id=u.id, token=token, expires_at=expires)
    db.add(pr)
    db.commit()
    background_tasks.add_task(send_recovery_email, u.correo, token)
    return mensaje

@app.post("/reset-password/{token}", tags=["Usuarios"])
def reset_password(token: str, req: PasswordResetRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordResetDB).filter(PasswordResetDB.token == token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    u = db.get(UsuarioDB, pr.user_id)
    u.contraseña_hash = pwd_context.hash(req.nueva_contraseña)
    db.delete(pr)
    db.commit()
    return {"mensaje": "Contraseña reestablecida correctamente"}


# --- Recuperación de contraseña ---
@app.post("/password-recovery", tags=["Usuarios"])
def password_recovery(req: PasswordRecoveryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    u = db.query(UsuarioDB).filter(UsuarioDB.correo == req.correo).first()
    mensaje = {"mensaje":"Si el correo existe, recibirás instrucciones por email."}
    if not u:
        return mensaje
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=1)
    pr = PasswordResetDB(user_id=u.id, token=token, expires_at=expires)
    db.add(pr); db.commit()
    background_tasks.add_task(send_recovery_email, u.correo, token)
    return mensaje

@app.post("/reset-password/{token}", tags=["Usuarios"])
def reset_password(token: str, req: PasswordResetRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordResetDB).filter(PasswordResetDB.token == token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(400, "Token inválido o expirado")
    u = db.get(UsuarioDB, pr.user_id)
    u.contraseña_hash = pwd_context.hash(req.nueva_contraseña)
    db.delete(pr); db.commit()
    return {"mensaje":"Contraseña reestablecida correctamente"}

# --- Rutas Presupuestos ---
@app.get("/presupuestos", response_model=List[PresupuestoRead], tags=["Presupuestos"])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(PresupuestoDB).all()

@app.get("/presupuestos/{presupuesto_id}", response_model=PresupuestoRead, tags=["Presupuestos"])
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    p = db.query(PresupuestoDB).get(presupuesto_id)
    if not p:
        raise HTTPException(404, "Presupuesto no encontrado")
    return p

@app.post("/presupuestos", response_model=PresupuestoRead, status_code=201, tags=["Presupuestos"])
def crear_presupuesto(p: PresupuestoCreate, db: Session = Depends(get_db)):
    nuevo = PresupuestoDB(**p.dict())
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return nuevo

@app.put("/presupuestos/{presupuesto_id}", response_model=PresupuestoRead, tags=["Presupuestos"])
def actualizar_presupuesto(presupuesto_id: int, datos: PresupuestoCreate, db: Session = Depends(get_db)):
    obj = db.query(PresupuestoDB).get(presupuesto_id)
    if not obj:
        raise HTTPException(404, "Presupuesto no encontrado")
    for k,v in datos.dict().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@app.delete("/presupuestos/{presupuesto_id}", status_code=204, tags=["Presupuestos"])
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    obj = db.query(PresupuestoDB).get(presupuesto_id)
    if not obj:
        raise HTTPException(404, "Presupuesto no encontrado")
    db.delete(obj); db.commit()

# --- Rutas Transacciones ---
@app.get("/transacciones", response_model=List[TransaccionRead], tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(TransaccionDB).all()

@app.get("/transacciones/{transaccion_id}", response_model=TransaccionRead, tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    t = db.query(TransaccionDB).get(transaccion_id)
    if not t:
        raise HTTPException(404, "Transacción no encontrada")
    return t

@app.post("/transacciones", response_model=TransaccionRead, status_code=201, tags=["Transacciones"])
def crear_transaccion(tr: TransaccionCreate, db: Session = Depends(get_db)):
    nuevo = TransaccionDB(**tr.dict())
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return nuevo

@app.put("/transacciones/{transaccion_id}", response_model=TransaccionRead, tags=["Transacciones"])
def actualizar_transaccion(transaccion_id: int, tr: TransaccionCreate, db: Session = Depends(get_db)):
    obj = db.query(TransaccionDB).get(transaccion_id)
    if not obj:
        raise HTTPException(404, "Transacción no encontrada")
    for k,v in tr.dict().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@app.delete("/transacciones/{transaccion_id}", status_code=204, tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    obj = db.query(TransaccionDB).get(transaccion_id)
    if not obj:
        raise HTTPException(404, "Transacción no encontrada")
    db.delete(obj); db.commit()

# --- Rutas Pagos Fijos ---
@app.get("/pagos-fijos", response_model=List[PagoFijoRead], tags=["Pagos Fijos"])
def listar_pagos_fijos(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(PagoFijoDB)
    if usuario_id:
        q = q.filter(PagoFijoDB.usuario_id == usuario_id)
    return q.all()

@app.get("/pagos-fijos/{pago_id}", response_model=PagoFijoRead, tags=["Pagos Fijos"])
def obtener_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    p = db.query(PagoFijoDB).get(pago_id)
    if not p:
        raise HTTPException(404, "Pago fijo no encontrado")
    return p

@app.post("/pagos-fijos", response_model=PagoFijoRead, status_code=201, tags=["Pagos Fijos"])
def crear_pago_fijo(pf: PagoFijoCreate, db: Session = Depends(get_db)):
    if not db.query(UsuarioDB).get(pf.usuario_id):
        raise HTTPException(404, "Usuario no encontrado")
    nuevo = PagoFijoDB(**pf.dict())
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return nuevo

@app.put("/pagos-fijos/{pago_id}", response_model=PagoFijoRead, tags=["Pagos Fijos"])
def actualizar_pago_fijo(pago_id: int, pf: PagoFijoCreate, db: Session = Depends(get_db)):
    obj = db.query(PagoFijoDB).get(pago_id)
    if not obj:
        raise HTTPException(404, "Pago fijo no encontrado")
    for k,v in pf.dict().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@app.delete("/pagos-fijos/{pago_id}", status_code=204, tags=["Pagos Fijos"])
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    obj = db.query(PagoFijoDB).get(pago_id)
    if not obj:
        raise HTTPException(404, "Pago fijo no encontrado")
    db.delete(obj); db.commit()

# --- Gráficas y resumen financiero ---
MESES_ES = {
    1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
    7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
}

@app.get("/graficas/categorias", response_model=List[CategoriaTotal], tags=["Gráficas"])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    tot = defaultdict(float)
    trans = db.query(TransaccionDB).join(CategoriaDB).filter(
        TransaccionDB.usuario_id==usuario_id,
        TransaccionDB.tipo==tipo
    ).all()
    for t in trans:
        tot[t.categoria.nombre] += t.monto
    return [{"categoria":c,"total":s} for c,s in tot.items()]

@app.get("/graficas/tendencias", response_model=List[TendenciaMensual], tags=["Gráficas"])
def tendencias_mensuales(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    tot_mes = defaultdict(float)
    for t in db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id==usuario_id,
        TransaccionDB.tipo==tipo
    ):
        tot_mes[t.fecha.month] += t.monto
    return [{"mes":MESES_ES[m],"total":tot_mes[m]} for m in sorted(tot_mes)]

@app.get("/resumen", response_model=ResumenFinanciero, tags=["Resumen Financiero"])
def resumen_financiero(usuario_id: int = 1, db: Session = Depends(get_db)):
    ing = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id==usuario_id,
        TransaccionDB.tipo=="ingreso"
    ).all()
    eg = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id==usuario_id,
        TransaccionDB.tipo=="gasto"
    ).all()
    total_ing = sum(t.monto for t in ing)
    total_eg  = sum(t.monto for t in eg)
    return {"total_ingresos":total_ing,"total_egresos":total_eg,"balance":total_ing-total_eg}
