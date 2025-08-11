# routes.py
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime, date, timedelta
from typing import List, Optional
from collections import defaultdict
from database import get_db
from models import Notificacion, PasswordReset, Usuario, Presupuesto, Transaccion, PagoFijo, Categoria
from schemas import (
    NotificacionRead, PasswordResetRequest, UsuarioBase, UsuarioCreate, Usuario as SchemaUsuario, UsuarioLogin, 
    PresupuestoBase, PresupuestoCreate, Presupuesto as SchemaPresupuesto, 
    TransaccionBase, TransaccionCreate, Transaccion as SchemaTransaccion, 
    PagoFijoBase, PagoFijoCreate, PagoFijo as SchemaPagoFijo, 
    CategoriaTotal, TendenciaMensual, ResumenFinanciero, UsuarioRead
)
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Endpoints de Usuarios
@router.post("/register", response_model=SchemaUsuario, tags=["Usuarios"])
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    user_in_db_email = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if user_in_db_email:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user_in_db_username = db.query(Usuario).filter(Usuario.nombre_usuario == user.nombre_usuario).first()
    if user_in_db_username:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")

    hashed_password = pwd_context.hash(user.contraseña)
    nuevo_usuario = Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña=hashed_password,
        telefono=user.telefono,
        esta_activo=True,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.put("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, datos: UsuarioBase, db: Session = Depends(get_db)):
    u = db.query(Usuario).get(usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    u.nombre_usuario = datos.nombre_usuario
    u.correo = datos.correo
    u.telefono = datos.telefono

    db.commit()
    db.refresh(u)
    return u

@router.post("/login", tags=["Usuarios"])
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if not usuario or not pwd_context.verify(user.contraseña_hash, usuario.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario.nombre_usuario,
        "usuario_id": usuario.id
    }

@router.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    u = db.query(Usuario).get(usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u


@router.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# --- Recuperación de contraseña ---
# Función simulada de envío de correo electrónico
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")

@router.post("/password-recovery", tags=["Usuarios"])
def password_recovery(
    req: PasswordRecoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    u = db.query(Usuario).filter(Usuario.correo == req.correo).first()
    mensaje = {"mensaje": "Si el correo existe, recibirás instrucciones por email."}
    if not u:
        return mensaje
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=1)
    pr = PasswordReset(user_id=u.id, token=token, expires_at=expires)
    db.add(pr); db.commit()
    background_tasks.add_task(send_recovery_email, u.correo, token)
    return mensaje

@router.post("/reset-password/{token}", tags=["Usuarios"])
def reset_password(token: str, req: PasswordResetRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordReset).filter(PasswordReset.token == token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    u = db.get(Usuario, pr.user_id)
    u.contraseña = req.nueva_contraseña
    db.delete(pr)
    db.commit()
    return {"mensaje": "Contraseña reestablecida correctamente"}

@router.post("/reset-password/{token}", tags=["Usuarios"])
def reset_password(token: str, req: PasswordResetRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordReset).filter(PasswordReset.token == token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    u = db.get(Usuario, pr.user_id)
    u.contraseña_hash = pwd_context.hash(req.nueva_contraseña)
    db.delete(pr)
    db.commit()
    return {"mensaje": "Contraseña reestablecida correctamente"}


# Endpoints de Presupuestos
@router.get("/presupuestos", response_model=List[SchemaPresupuesto], tags=["Presupuestos"])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(Presupuesto).all()

@router.get("/presupuestos/{presupuesto_id}", response_model=SchemaPresupuesto, tags=["Presupuestos"])
def obtener_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return presupuesto

@router.post("/presupuestos", response_model=SchemaPresupuesto, tags=["Presupuestos"])
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = Presupuesto(**presupuesto.dict())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@router.put("/presupuestos/{presupuesto_id}", response_model=SchemaPresupuesto, tags=["Presupuestos"])
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

# Endpoints de Transacciones
@router.get("/transacciones", response_model=List[SchemaTransaccion], tags=["Transacciones"])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(Transaccion).all()

@router.get("/transacciones/{transaccion_id}", response_model=SchemaTransaccion, tags=["Transacciones"])
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@router.post("/transacciones", response_model=SchemaTransaccion, tags=["Transacciones"])
def agregar_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = Transaccion(**transaccion.dict())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.put("/transacciones/{transaccion_id}", response_model=SchemaTransaccion, tags=["Transacciones"])
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

# Endpoints de Pagos Fijos
@router.get("/pagos-fijos", response_model=List[SchemaPagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(PagoFijo)
    if usuario_id:
        query = query.filter(PagoFijo.usuario_id == usuario_id)
    return query.all()

@router.get("/pagos-fijos/{pago_id}", response_model=SchemaPagoFijo, tags=["Pagos Fijos"])
def obtener_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(PagoFijo).filter(PagoFijo.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    return pago

@router.post("/pagos-fijos", response_model=SchemaPagoFijo, tags=["Pagos Fijos"])
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

@router.put("/pagos-fijos/{pago_id}", response_model=SchemaPagoFijo, tags=["Pagos Fijos"])
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

@router.get("/usuarios/{usuario_id}/pagos-fijos", response_model=List[SchemaPagoFijo], tags=["Pagos Fijos"])
def listar_pagos_fijos_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return db.query(PagoFijo).filter(PagoFijo.usuario_id == usuario_id).all()

# Endpoints de Gráficas y Reportes
@router.get("/graficas/categorias", response_model=List[CategoriaTotal], tags=["Gráficas"])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    totales = defaultdict(float)
    transacciones_con_categorias = db.query(Transaccion, Categoria.nombre).join(
        Categoria, Transaccion.categoria_id == Categoria.id
    ).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.tipo == tipo
    ).all()

    for t, categoria_nombre in transacciones_con_categorias:
        if categoria_nombre:
            totales[categoria_nombre] += t.monto

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
        Transaccion.tipo == "gasto"
    ).all()
    
    total_ingresos = sum(t.monto for t in ingresos)
    total_egresos = sum(t.monto for t in egresos)
    balance = total_ingresos - total_egresos

    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance
    }
    
    # --- Rutas Notificaciones ---
@router.get("/notificaciones", response_model=List[NotificacionRead], tags=["Notificaciones"])
def listar_notificaciones(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Notificacion)
    if usuario_id is not None:
        q = q.filter(Notificacion.usuario_id == usuario_id)
    return q.all()

@router.get("/notificaciones/{notif_id}", response_model=NotificacionRead, tags=["Notificaciones"])
def obtener_notificacion(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notificacion).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return n

@router.post("/notificaciones", response_model=NotificacionRead, status_code=201, tags=["Notificaciones"])
def crear_notificacion(payload: NotificacionCreate, db: Session = Depends(get_db)):
    if not db.query(Usuario).get(payload.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    n = Notificacion(**payload.dict())
    db.add(n); db.commit(); db.refresh(n)
    return n

@router.put("/notificaciones/{notif_id}", response_model=NotificacionRead, tags=["Notificaciones"])
def actualizar_notificacion(notif_id: int, datos: NotificacionCreate, db: Session = Depends(get_db)):
    n = db.query(Notificacion).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    for k, v in datos.dict().items():
        setattr(n, k, v)
    db.commit(); db.refresh(n)
    return n

@router.delete("/notificaciones/{notif_id}", status_code=204, tags=["Notificaciones"])
def eliminar_notificacion(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notificacion).get(notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(n); db.commit()

