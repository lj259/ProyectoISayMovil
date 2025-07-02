from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Presupuesto(Base):
    __tablename__ = "presupuestos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    monto = Column(Float)
    ano =Column(Integer)
    mes = Column(Integer)
    fecha_creacion = Column(Date)
    fecha_actualizacion = Column(Date)

    categoria = relationship("Categoria")