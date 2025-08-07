# SQLAlchemy core + func.now()
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DECIMAL, TIMESTAMP, Enum, func
from database import Base


# --- Modelos SQLAlchemy ---

class Usuario(Base):
    __tablename__ = "usuarios"
    id                  = Column(Integer, primary_key=True, index=True)
    nombre_usuario      = Column(String(50), unique=True, nullable=False)
    correo              = Column(String(100), unique=True, nullable=False)
    contraseña_hash     = Column(String(255), nullable=False)  # texto claro
    telefono            = Column(String(20), nullable=True)
    esta_activo         = Column(Boolean, default=True)
    fecha_creacion      = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(),
                                onupdate=func.now(), nullable=False)
    
class CategoriaDB(Base):
    __tablename__ = "categorias"
    id                = Column(Integer, primary_key=True, index=True)
    nombre            = Column(String(50), nullable=False)
    tipo              = Column(Enum('ingreso', 'egreso'), nullable=False)
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
    tipo           = Column(Enum('ingreso','egreso', 'ahorro'), nullable=False)
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