from datetime import date
from pydantic import BaseModel, validator
class PresupuestoCreate(BaseModel):
    categoria_id: int
    monto: float
    ano :int
    mes:int
    @validator('monto')
    def validate_monto(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return v
    class PresupuestoResponse(BaseModel):
     id: int
    categoria_id: int
    categoria_nombre: str
    monto: float
    ano: int
    mes: int
    mes_nombre: str
    fecha_creacion: date
    
    class Config:
     from_attributes = True