from datetime import date
from pydantic import BaseModel, validator
class PresupuestoCreate(BaseModel):
    categoria_id: int
    monto: float
    año :int
    mes:int
    @validator('monto')
    def validate_monto(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return v