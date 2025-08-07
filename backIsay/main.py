# ——— Imports de terceros —————————————————————————————————————
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  
from typing import List
from collections import defaultdict
from datetime import datetime
# SQLAlchemy ORM
from sqlalchemy.orm import Session

import models, schemas
from schemas import *
from database import *

# Inicialización de la app
app = FastAPI(title="LanaApp API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función simulada de envío de correo electrónico
def send_recovery_email(email: str, token: str):
    print(f"[EMAIL] Para {email}: usa este token → {token}")


MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

#  Endpoint 1: Gráfico circular



@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total por categoría según el tipo (ingreso, egreso, ahorro)
    """
    totales = defaultdict(float)

    transacciones = db.query(TransaccionDB).join(CategoriaDB, isouter=True).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == tipo
    ).all()

    for t in transacciones:
        # Si la transacción no tiene categoría_id usamos tipo (Ingreso/Gasto)
        if t.categoria and t.categoria.nombre:
            totales[t.categoria.nombre] += t.monto
        else:
            totales[t.tipo.capitalize()] += t.monto

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

# Endpoint 2: Gráfico de barras



@app.get("/graficas/tendencias", response_model=List[TendenciaMensual])
def tendencias_mensuales(tipo: str, usuario_id: int = 1, db: Session = Depends(get_db)):
    """
    Devuelve total mensual por tipo (ingreso, egreso, ahorro)
    """
    totales_por_mes = defaultdict(float)

    transacciones = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == tipo
    ).all()

    for t in transacciones:
        if t.fecha:
            mes = t.fecha.month
            totales_por_mes[mes] += t.monto

    return [
        {"mes": MESES_ES[mes], "total": totales_por_mes[mes]}
        for mes in sorted(totales_por_mes.keys())
    ] 

# Endpoint 3: Resumen financiero



@app.get("/resumen", response_model=ResumenFinanciero)
def resumen_financiero(usuario_id: int = 1, db: Session = Depends(get_db)):

    ingresos = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "ingreso"
    ).all()

    egresos = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "egreso"
    ).all()

    ahorros = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id,
        TransaccionDB.tipo == "ahorro"
    ).all()
    
    total_ingresos = sum(t.monto for t in ingresos)
    total_egresos = sum(t.monto for t in egresos)
    total_ahorros = sum(t.monto for t in ahorros)
    balance = total_ingresos - total_egresos + total_ahorros

    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "total_ahorros": total_ahorros,
        "balance": balance
    } 

# Endpoint 4: Transacciones (Listar)




@app.get("/transacciones", response_model=List[TransaccionOut])
def listar_transacciones(usuario_id: int = 1, db: Session = Depends(get_db)):
    transacciones = db.query(TransaccionDB).filter(
        TransaccionDB.usuario_id == usuario_id
    ).all()

    return [
        {
            "id": t.id,
            "monto": t.monto,
            "tipo": t.tipo,
            "descripcion": t.descripcion,
            "fecha": t.fecha.strftime("%Y-%m-%d") if t.fecha else "",
            "categoria": t.tipo.capitalize()
        }
        for t in transacciones
    ]



@app.post("/transacciones")
def crear_transaccion(data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    print(f"Creando transacción: {data}")
    nueva_transaccion = TransaccionDB(
        usuario_id=usuario_id,
        monto=data.monto,
        tipo=data.tipo.lower(),
        descripcion=data.descripcion,
        fecha=data.fecha,
        categoria_id=data.categoria_id,
        fecha_creacion=datetime.now().date(),
        es_recurrente=False,
        id_recurrente=None
    )
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    return {"mensaje": "Transacción creada correctamente", "id": nueva_transaccion.id}

@app.put("/transacciones/{id}")
def editar_transaccion(id: int, data: TransaccionCreate, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == id, TransaccionDB.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    transaccion.monto = data.monto
    transaccion.tipo = data.categoria.lower()
    transaccion.descripcion = data.descripcion
    transaccion.fecha = datetime.strptime(data.fecha, "%Y-%m-%d").date()
    db.commit()
    db.refresh(transaccion) 
    return {"mensaje": "Transacción actualizada correctamente"}

@app.delete("/transacciones/{id}")
def eliminar_transaccion(id: int, usuario_id: int = 1, db: Session = Depends(get_db)):
    transaccion = db.query(TransaccionDB).filter(TransaccionDB.id == id, TransaccionDB.usuario_id == usuario_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(transaccion)
    db.commit()
    return {"mensaje": "Transacción eliminada correctamente"}


# --- Endpoints Usuarios ---
# 📝 REGISTRO
@app.post("/register")
def register(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_in_db = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = pwd_context.hash(user.password)

    nuevo_usuario = models.Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña=hashed_password,
        telefono=user.telefono
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"mensaje": "Usuario registrado exitosamente", "usuario_id": nuevo_usuario.id}

# 🔐 LOGIN
@app.post("/login")
def login(user: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()

    if not usuario or not pwd_context.verify(user.password, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "mensaje": "Inicio de sesión exitoso",
        "usuario_id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "correo": usuario.correo
    }