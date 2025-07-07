from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

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