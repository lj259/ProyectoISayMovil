from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, date
from typing import List, Optional
from collections import defaultdict
from database import get_db
from models import Usuario, Presupuesto, Transaccion, PagoFijo, Categoria
from schemas import (
    UsuarioCreate, Usuario, UsuarioLogin,
    PresupuestoBase, PresupuestoCreate, Presupuesto,
    TransaccionBase, TransaccionCreate, Transaccion,
    PagoFijoBase, PagoFijoCreate, PagoFijo,
    CategoriaTotal, TendenciaMensual, ResumenFinanciero
)
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

@router.post("/register", response_model=Usuario, tags=["Usuarios"])
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    user_in_db = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Hashear la contraseña
    hashed_password = pwd_context.hash(user.contraseña)
    
    # Crear nuevo usuario con el modelo SQLAlchemy
    nuevo_usuario = models.Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña=hashed_password,
        telefono=user.telefono,
        esta_activo=True,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    
    # Guardar en la base de datos
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@router.post("/login", tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if not usuario or not pwd_context.verify(user.contraseña, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario.nombre_usuario,
        "usuario_id": usuario.id
    }

@router.get("/presupuestos", response_model=List[Presupuesto], tags=["Presupuestos"])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(Presupuesto).all()

@router.get("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return presupuesto

@router.post("/presupuestos", response_model=Presupuesto, tags=["Presupuestos"])
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = Presupuesto(**presupuesto.dict())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@router.put("/presupuestos/{presupuesto_id}", response_model=Presupuesto, tags=["Presupuestos"])
def actualizar_presupuesto(presupuesto_id: int, presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    for key, value in presupuesto.dict().items():
        setattr(db_presupuesto, key, value)
    
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@router.delete("/presupuestos/{presupuesto_id}", tags=["Presupuestos"])
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    db.delete(db_presupuesto)
    db.commit()
    return {"mensaje": "Presupuesto eliminado correctamente"}

@router.get("/transacciones", response_model=List[Transaccion], tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(Transaccion).all()

@router.get("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@router.post("/transacciones", response_model=Transaccion, tags=["Transacciones"])
def agregar_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = Transaccion(**transaccion.dict())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.put("/transacciones/{transaccion_id}", response_model=Transaccion, tags=["Transacciones"])
def actualizar_transaccion(transaccion_id: int, transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    for key, value in transaccion.dict().items():
        setattr(db_transaccion, key, value)
    
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    db.delete(db_transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}

@router.get("/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(PagoFijo)
    if usuario_id:
        query = query.filter(PagoFijo.usuario_id == usuario_id)
    return query.all()

@router.get("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def obtener_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    return pago

@router.post("/pagos-fijos", response_model=PagoFijo, tags=["Pagos Fijos"])
def crear_pago_fijo(pago: PagoFijoCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    existe_pago = db.query(PagoFijo).filter(
        PagoFijo.descripcion == pago.descripcion,
        PagoFijo.usuario_id == pago.usuario_id,
        PagoFijo.monto == pago.monto
    ).first()
    
    if existe_pago:
        raise HTTPException(status_code=400, detail="Ya existe un pago fijo similar para este usuario")
    
    db_pago = PagoFijo(**pago.dict())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.put("/pagos-fijos/{pago_id}", response_model=PagoFijo, tags=["Pagos Fijos"])
def actualizar_pago_fijo(pago_id: int, pago: PagoFijoCreate, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for key, value in pago.dict().items():
        setattr(db_pago, key, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.delete("/pagos-fijos/{pago_id}", tags=["Pagos Fijos"])
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    
    db.delete(db_pago)
    db.commit()
    return {"mensaje": "Pago fijo eliminado correctamente"}

@router.get("/usuarios/{usuario_id}/pagos-fijos", response_model=List[PagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return db.query(PagoFijo).filter(PagoFijo.usuario_id == usuario_id).all()

@router.get("/")
def home():
    return {"message": "Bienvenido a la API de LanaApp"}

@router.get("/graficas/categorias", response_model=List[CategoriaTotal], tags=["Gráficas"])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    totales = defaultdict(float)

    transacciones = db.query(Transaccion).join(Categoria).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

@router.get("/graficas/tendencias", response_model=List[TendenciaMensual], tags=["Gráficas"])
def tendencias_mensuales(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    totales_por_mes = defaultdict(float)

    transacciones = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t in transacciones:
        if t.fecha:
            mes = t.fecha.month
            totales_por_mes[mes] += t.monto

    return [
        {"mes": MESES_ES[mes], "total": totales_por_mes[mes]}
        for mes in sorted(totales_por_mes.keys())
    ] 

@router.get("/resumen", response_model=ResumenFinanciero, tags=["Resumen Financiero"])
def resumen_financiero(usuario_id: int = 1, db: Session = Depends(get_db)):
    ingresos = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "ingreso"
    ).all()
    
    egresos = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == "egreso"
    ).all()
    
    total_ingresos = sum(t.monto for t in ingresos)
    total_egresos = sum(t.monto for t in egresos)
    balance = total_ingresos - total_egresos

    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance
    }