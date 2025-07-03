from pydantic import BaseModel, EmailStr

# Datos necesarios para REGISTRAR usuario
class UsuarioCreate(BaseModel):
    nombre_usuario: str
    correo: EmailStr
    contraseña: str
    telefono: str | None = None

# Datos necesarios para LOGIN
class UsuarioLogin(BaseModel):
    correo: EmailStr
    contraseña: str
