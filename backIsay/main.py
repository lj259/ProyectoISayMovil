from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
<<<<<<< Updated upstream
=======

from typing import List
from fastapi import HTTPException, Depends, BackgroundTasks
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
>>>>>>> Stashed changes
from sqlalchemy import (
    create_engine, Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import date, datetime
from passlib.context import CryptContext
from collections import defaultdict

<<<<<<< Updated upstream
=======
from typing import Literal, Optional, List
from datetime import datetime


# Función simulada de envío de correo electrónico
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")

# --- Configuración de la base de datos ---
>>>>>>> Stashed changes
DATABASE_URL = "mysql+pymysql://root:@localhost/lanaapp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
=======

# --- Schemas Pydantic ---

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
class Usuario(UsuarioBase):
=======
class UsuarioRead(BaseModel):
>>>>>>> Stashed changes
    id: int
    nombre_usuario: str
    correo: str
    telefono: Optional[str]
    esta_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True



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
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="LanaApp API", version="1.0.0")

<<<<<<< Updated upstream
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
=======

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
>>>>>>> Stashed changes
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/login",tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
<<<<<<< Updated upstream
    usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if not usuario or not pwd_context.verify(user.contraseña, usuario.contraseña):
=======
    u = db.query(UsuarioDB).filter(UsuarioDB.correo == user.correo).first()
    if not u or u.contraseña != user.contraseña:  # simple comparación
>>>>>>> Stashed changes
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario.nombre_usuario,
        "usuario_id": usuario.id
    }

<<<<<<< Updated upstream
=======
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

>>>>>>> Stashed changes
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

# --- Rutas de Resumen Financiero ---

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

#  Endpoint 1: Gráfico circular

@app.get("/graficas/categorias", response_model=List[CategoriaTotal], tags=["Gráficas"])
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

@app.get("/graficas/tendencias", response_model=List[TendenciaMensual], tags=["Gráficas"])
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

@app.get("/resumen", response_model=ResumenFinanciero , tags=["Resumen Financiero"])
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

