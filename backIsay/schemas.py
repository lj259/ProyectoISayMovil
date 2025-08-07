from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, date

# --- Usuarios ---
class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: EmailStr
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

# --- Presupuestos ---
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

# --- Transacciones ---
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
        
class TransaccionOut(BaseModel):
    id: int
    monto: float
    tipo: str
    descripcion: str
    fecha: str
    categoria: str

    class Config:
        orm_mode = True
        
# --- Pagos Fijos ---
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

# --- Categorias ---
class CategoriaTotal(BaseModel):
    categoria: str
    total: float


class TendenciaMensual(BaseModel):
    mes: str
    total: float
    
class ResumenFinanciero(BaseModel):
    total_ingresos: float
    total_egresos: float
    total_ahorros: float
    balance: float

# --- Notificaciones ---
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
       
