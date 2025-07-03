from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"  # Nombre real de la tabla

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    esta_activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP)
    fecha_actualizacion = Column(TIMESTAMP)
