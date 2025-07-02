from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.presupuesto import Presupuesto
from models.categoria import Categoria
from schemas.presupuesto_schemas import PresupuestoCreate, PresupuestoUpdate

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

class PresupuestoService:

    @staticmethod
    def crear_presupuesto(db: Session, presupuesto: PresupuestoCreate, usuario_id: int):
        try:
            # Verificar que la categoría existe y pertenece al usuario
            categoria = db.query(Categoria).filter(
                Categoria.id == presupuesto.categoria_id,
                Categoria.usuario_id == usuario_id
            ).first()
            if not categoria:
                raise HTTPException(
                    status_code=404,
                    detail="Categoría no encontrada"
                )

            # Verificar que no existe presupuesto para esta combinación
            existente = db.query(Presupuesto).filter(
                Presupuesto.usuario_id == usuario_id,
                Presupuesto.categoria_id == presupuesto.categoria_id,
                Presupuesto.mes == presupuesto.mes,
                Presupuesto.ano == presupuesto.ano,
            ).first()
            if existente:
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un presupuesto para esta categoría y mes"
                )

            # Crear el presupuesto
            nuevo_presupuesto = Presupuesto(
                usuario_id=usuario_id,
                categoria_id=presupuesto.categoria_id,
                monto=presupuesto.monto,
                ano=presupuesto.ano,
                mes=presupuesto.mes,
                fecha_creacion=datetime.now().date()
            )
            db.add(nuevo_presupuesto)
            db.commit()
            db.refresh(nuevo_presupuesto)

            return {
                "id": nuevo_presupuesto.id,
                "categoria_id": nuevo_presupuesto.categoria_id,
                "categoria_nombre": categoria.nombre,
                "monto": nuevo_presupuesto.monto,
                "ano": nuevo_presupuesto.ano,
                "mes": nuevo_presupuesto.mes,
                "mes_nombre": MESES_ES[nuevo_presupuesto.mes],
                "fecha_creacion": nuevo_presupuesto.fecha_creacion
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @staticmethod
    def listar_presupuestos(db: Session, usuario_id: int, ano=None, mes=None, categoria_id=None):
        try:
            query = db.query(Presupuesto).join(Categoria).filter(
                Presupuesto.usuario_id == usuario_id
            )

            if ano:
                query = query.filter(Presupuesto.ano == ano)
            if mes:
                if not 1 <= mes <= 12:
                    raise HTTPException(status_code=400, detail="Mes inválido")
                query = query.filter(Presupuesto.mes == mes)
            if categoria_id:
                query = query.filter(Presupuesto.categoria_id == categoria_id)

            presupuestos = query.all()
            resultado = []
            for p in presupuestos:
                resultado.append({
                    "id": p.id,
                    "categoria_id": p.categoria_id,
                    "categoria_nombre": p.categoria.nombre,
                    "monto": p.monto,
                    "ano": p.ano,
                    "mes": p.mes,
                    "mes_nombre": MESES_ES[p.mes],
                    "fecha_creacion": p.fecha_creacion
                })

            return resultado

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @staticmethod
    def actualizar_presupuesto(db: Session, presupuesto_id: int, presupuesto_data: PresupuestoUpdate, usuario_id: int):
        try:
            # Buscar el presupuesto
            presupuesto = db.query(Presupuesto).filter(
                Presupuesto.id == presupuesto_id,
                Presupuesto.usuario_id == usuario_id
            ).first()

            if not presupuesto:
                raise HTTPException(
                    status_code=404,
                    detail="Presupuesto no encontrado"
                )

            # Actualizar
            presupuesto.monto = presupuesto_data.monto
            presupuesto.fecha_actualizacion = datetime.now().date()

            db.commit()
            db.refresh(presupuesto)
            return {
                "id": presupuesto.id,
                "categoria_id": presupuesto.categoria_id,
                "categoria_nombre": presupuesto.categoria.nombre,
                "monto": presupuesto.monto,
                "ano": presupuesto.ano,
                "mes": presupuesto.mes,
                "mes_nombre": MESES_ES[presupuesto.mes],
                "fecha_creacion": presupuesto.fecha_creacion,
                "fecha_actualizacion": presupuesto.fecha_actualizacion
            }
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @staticmethod
    def eliminar_presupuesto(db: Session, presupuesto_id: int, usuario_id: int):
        try:
            presupuesto = db.query(Presupuesto).filter(
                Presupuesto.id == presupuesto_id,
                Presupuesto.usuario_id == usuario_id
            ).first()

            if not presupuesto:
                raise HTTPException(
                    status_code=404,
                    detail="Presupuesto no encontrado"
                )

            db.delete(presupuesto)
            db.commit()
            return {"message": "Presupuesto eliminado exitosamente"}

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno del servidor")
