from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.presupuesto_schemas import PresupuestoCreate, PresupuestoUpdate, PresupuestoResponse
from services.presupuesto_service import PresupuestoService

router = APIRouter(prefix="/presupuestos", tags=["presupuestos"])
@router.post("/", response_model=PresupuestoResponse)
def crear_presupuesto(
    presupuesto: PresupuestoCreate, 
    usuario_id: int = 1, 
):
     return PresupuestoService.crear_presupuesto(db, presupuesto, usuario_id)

@router.get("/", response_model=List[PresupuestoResponse])
def listar_presupuestos(
    ano: int = None,
    mes: int = None,
    categoria_id: int = None,
    usuario_id: int = 1
    ):
    return PresupuestoService.listar_presupuestos(db, usuario_id, ano, mes, categoria_id)
@router.put("/{presupuesto_id}", response_model=PresupuestoResponse)
def actualizar_presupuesto(
    presupuesto_id: int,
    presupuesto_data: PresupuestoUpdate,
    usuario_id: int = 1,
    ):
    return PresupuestoService.actualizar_presupuesto(db, presupuesto_id, presupuesto_data, usuario_id)
@router.delete("/{presupuesto_id}")
def eliminar_presupuesto(
    presupuesto_id: int,
    usuario_id: int = 1,
    ):
    return PresupuestoService.eliminar_presupuesto(db, presupuesto_id, usuario_id)