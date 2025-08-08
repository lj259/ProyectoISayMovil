# ——— Imports de terceros —————————————————————————————————————
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  
from typing import List
from collections import defaultdict
from datetime import datetime
# SQLAlchemy ORM
from sqlalchemy.orm import Session

import models, schemas
from models import *
from schemas import *
from database import *

# Inicialización de la app
app = FastAPI(title="LanaApp API", version="1.0.0")


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

# Función simulada de envío de correo electrónico
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")


MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

#  Endpoint 1: Gráfico circular



@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total por categoría según el tipo (ingreso, egreso, ahorro)
    """
    totales = defaultdict(float)

    transacciones = db.query(TransaccionDB).join(CategoriaDB, isouter=True).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == tipo
    ).all()

    for t in transacciones:
        # Si la transacción no tiene categoría_id usamos tipo (Ingreso/Gasto)
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto
        else:
            totales[t.tipo.capitalize()] += t.monto

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

# Endpoint 2: Gráfico de barras



@app.get("/graficas/tendencias", response_model=List[TendenciaMensual])
def tendencias_mensuales(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total mensual por tipo (ingreso, egreso, ahorro)
    """
    totales_por_mes = defaultdict(float)

    transacciones = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == tipo
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

    ingresos = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "ingreso"
    ).all()

    egresos = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "egreso"
    ).all()

    ahorros = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "ahorro"
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

# Endpoint 4: Transacciones (Listar)




@app.get("/transacciones", response_model=List[TransaccionOut])
def listar_transacciones(usuario_id: int = 1, db: Session = Depends(get_db)):
    transacciones = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id
    ).all()

    return [
        {
            "id": t.id,
            "monto": t.monto,
            "tipo": t.tipo,
            "descripcion": t.descripcion,
            "fecha": t.fecha.strftime("%Y-%m-%d") if t.fecha else "",
            "categoria": t.tipo.capitalize()
        }
        for t in transacciones
    ]



@app.post("/transacciones")
def crear_transaccion(data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    print(f"Creando transacción: {data}")
    nueva_transaccion = TransaccionDB(
        usuario_id=usuario_id,
        monto=data.monto,
        tipo=data.tipo.lower(),
        descripcion=data.descripcion,
        fecha=data.fecha,
        categoria_id=data.categoria_id,
        fecha_creacion=datetime.now().date(),
        es_recurrente=False,
        id_recurrente=None
    )
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    return {"mensaje": "Transacción creada correctamente", "id": nueva_transaccion.id}

@app.put("/transacciones/{id}")
def editar_transaccion(id: int, data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == id, TransaccionDB.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    transaccion.monto = data.monto
    transaccion.tipo = data.categoria.lower()
    transaccion.descripcion = data.descripcion
    transaccion.fecha = datetime.strptime(data.fecha, "%Y-%m-%d").date()
    db.commit()
    db.refresh(transaccion) 
    return {"mensaje": "Transacción actualizada correctamente"}

@app.delete("/transacciones/{id}")
def eliminar_transaccion(id: int, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == id, TransaccionDB.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}


# --- Endpoints Usuarios ---
# 📝 REGISTRO
@app.post("/register")
def register(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    print(f"Registrando usuario: {user}")
    user_in_db = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = pwd_context.hash(user.contraseña_hash)

    nuevo_usuario = models.Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña_hash=hashed_password,
        telefono=user.telefono
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"mensaje": "Usuario registrado exitosamente", "usuario_id": nuevo_usuario.id}

# 🔐 LOGIN
@app.post("/login")
def login(user: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    print(f"Intento de login: {user}")
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    print(f"Usuario encontrado: {usuario}")
    if not usuario or not pwd_context.verify(user.contraseña_hash, usuario.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario_id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "correo": usuario.correo
    }
import uuid
from datetime import date, datetime, timedelta
from collections import defaultdict
from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

# SQLAlchemy core + func.now()
from sqlalchemy import (
    create_engine,
    Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean,
    func,
)
# SQLAlchemy ORM
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
)

from passlib.context import CryptContext

# ——— Configuración de BD —————————————————————————————————————
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()
pwd_context  = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Función simulada de envío de correo electrónico
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")



# --- Modelos SQLAlchemy ---
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id                  = Column(Integer, primary_key=True, index=True)
    nombre_usuario      = Column(String(50), unique=True, nullable=False)
    correo              = Column(String(100), unique=True, nullable=False)
    contraseña          = Column(String(255), nullable=False)  # texto claro
    telefono            = Column(String(20), nullable=True)
    esta_activo         = Column(Boolean, default=True)
    fecha_creacion      = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(),
                                onupdate=func.now(), nullable=False)
    
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

class NotificacionDB(Base):
    __tablename__ = "notificaciones"
    id               = Column(Integer, primary_key=True, index=True)
    usuario_id       = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo             = Column(Enum('correo','sms'), nullable=False)
    asunto           = Column(String(100), nullable=False)
    mensaje          = Column(String, nullable=False)
    fue_enviada      = Column(Boolean, default=False)
    fecha_creacion   = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_programada = Column(TIMESTAMP, nullable=True)
    fecha_envio      = Column(TIMESTAMP, nullable=True)

# Vuelve a crear tablas
Base.metadata.create_all(bind=engine)


# --- Schemas Pydantic ---

class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: str
    telefono: Optional[str] = None

class UsuarioCreate(BaseModel):
    nombre_usuario: str
    correo: str
    contraseña: str     
    telefono: Optional[str] = None

class UsuarioLogin(BaseModel):
    correo: str
    contraseña: str

class UsuarioRead(BaseModel):
    id: int
    nombre_usuario: str
    correo: str
    telefono: Optional[str]
    esta_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    class Config:
        orm_mode = True



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


class NotificacionBase(BaseModel):
    usuario_id: int
    tipo: Literal['correo','sms']
    asunto: str
    mensaje: str
    fecha_programada: Optional[datetime] = None

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionRead(NotificacionBase):
    id: int
    fue_enviada: bool
    fecha_creacion: datetime
    fecha_envio: Optional[datetime]
    class Config:
        orm_mode = True

    
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register", response_model=UsuarioRead, tags=["Usuarios"])
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(UsuarioDB).filter(UsuarioDB.correo == user.correo).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    nuevo = UsuarioDB(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña=user.contraseña,   # guardamos en texto claro
        telefono=user.telefono
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.post("/login", tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    u = db.query(UsuarioDB).filter(UsuarioDB.correo == user.correo).first()
    if not u or u.contraseña != user.contraseña:  # simple comparación
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
    db.add(pr); db.commit()
    background_tasks.add_task(send_recovery_email, u.correo, token)
    return mensaje

@app.post("/reset-password/{token}", tags=["Usuarios"])
def reset_password(token: str, req: PasswordResetRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordResetDB).filter(PasswordResetDB.token == token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    u = db.get(UsuarioDB, pr.user_id)
    u.contraseña = req.nueva_contraseña    
    db.delete(pr)
    db.commit()
    return {"mensaje": "Contraseña reestablecida correctamente"}

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

# --- Rutas Notificaciones ---
@app.get("/notificaciones", response_model=List[NotificacionRead], tags=["Notificaciones"])
def listar_notificaciones(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(NotificacionDB)
    if usuario_id is not None:
        q = q.filter(NotificacionDB.usuario_id == usuario_id)
    return q.all()

@app.get("/notificaciones/{notif_id}", response_model=NotificacionRead, tags=["Notificaciones"])
def obtener_notificacion(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(NotificacionDB).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return n

@app.post("/notificaciones", response_model=NotificacionRead, status_code=201, tags=["Notificaciones"])
def crear_notificacion(payload: NotificacionCreate, db: Session = Depends(get_db)):
    if not db.query(UsuarioDB).get(payload.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    n = NotificacionDB(**payload.dict())
    db.add(n); db.commit(); db.refresh(n)
    return n

@app.put("/notificaciones/{notif_id}", response_model=NotificacionRead, tags=["Notificaciones"])
def actualizar_notificacion(notif_id: int, datos: NotificacionCreate, db: Session = Depends(get_db)):
    n = db.query(NotificacionDB).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    for k, v in datos.dict().items():
        setattr(n, k, v)
    db.commit(); db.refresh(n)
    return n

@app.delete("/notificaciones/{notif_id}", status_code=204, tags=["Notificaciones"])
def eliminar_notificacion(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(NotificacionDB).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(n); db.commit()

@app.put("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, datos: UsuarioBase, db: Session = Depends(get_db)):
    u = db.query(UsuarioDB).get(usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    u.nombre_usuario = datos.nombre_usuario
    u.correo = datos.correo
    u.telefono = datos.telefono

    db.commit()
    db.refresh(u)
    return u
