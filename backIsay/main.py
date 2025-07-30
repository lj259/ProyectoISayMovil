from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
import schemas
from database import SessionLocal, engine, Base

app = FastAPI()

# 🔐 Middleware CORS (acepta desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes reemplazar con ["http://localhost:19006"] para Expo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔧 Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# 🔐 Encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔌 Conexión a BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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