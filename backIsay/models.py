from sqlalchemy import (
    Column, Integer, Float, DECIMAL, TIMESTAMP,
    ForeignKey, String, Date, Enum, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date

Base = declarative_base()

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