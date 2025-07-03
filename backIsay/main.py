from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
from database import SessionLocal, engine, Base




app = FastAPI()

# Crear las tablas si no existen (no borra nada si ya están)
Base.metadata.create_all(bind=engine)

# Esto sirve para encriptar la contraseña
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para obtener la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Endpoint para REGISTRO
@app.post("/register")
def register(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_in_db = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = pwd_context.hash(user.contraseña)
    nuevo_usuario = models.Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.correo,
        contraseña_hash=hashed_password,
        telefono=user.telefono
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado exitosamente", "usuario_id": nuevo_usuario.id}

# 🔹 Endpoint para LOGIN
@app.post("/login")
def login(user: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if not usuario or not pwd_context.verify(user.contraseña, usuario.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {"mensaje": "Inicio de sesión exitoso", "usuario_id": usuario.id}
