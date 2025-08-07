from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from typing import List
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship


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
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    tipo = Column(String(50))  # ahora usamos esto para guardar Ingreso/Gasto
    descripcion = Column(String(255))
    fecha = Column(Date)
    es_recurrente = Column(Boolean)
    id_recurrente = Column(Integer)
    fecha_creacion = Column(Date)

    categoria = relationship("Categoria", backref="transacciones")

app = FastAPI()
# ——— Imports de terceros —————————————————————————————————————
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

    transacciones = db.query(Transaccion).join(Categoria, isouter=True).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        # Si la transacción no tiene categoría_id usamos tipo (Ingreso/Gasto)
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto
        else:
            totales[t.tipo.capitalize()] += t.monto

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
    total_ahorros: float
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

# Endpoint 4: Transacciones (Listar)

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
            "categoria": t.tipo.capitalize()
        }
        for t in transacciones
    ]

class TransaccionCreate(BaseModel):
    monto: float
    categoria: str  # ingreso o egreso
    descripcion: str
    fecha: str  # YYYY-MM-DD

@app.post("/transacciones")
def crear_transaccion(data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    nueva_transaccion = Transaccion(
        usuario_id=usuario_id,
        monto=data.monto,
        tipo=data.categoria.lower(),
        descripcion=data.descripcion,
        fecha=datetime.strptime(data.fecha, "%Y-%m-%d").date(),
        categoria_id=None,
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
    transaccion = db.query(Transaccion).filter(Transaccion.id == id, Transaccion.usuario_id == usuario_id).first()
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
    transaccion = db.query(Transaccion).filter(Transaccion.id == id, Transaccion.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}