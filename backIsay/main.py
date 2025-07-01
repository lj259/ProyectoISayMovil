from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI()

# Simulamos una "base de datos"
transacciones = [
    {"id": 1, "usuario_id": 1, "monto": 1000, "tipo": "ingreso", "categoria": "Sueldo", "fecha": "2025-07-01"},
    {"id": 2, "usuario_id": 1, "monto": 500, "tipo": "egreso", "categoria": "Comida", "fecha": "2025-07-01"},
    {"id": 3, "usuario_id": 1, "monto": 200, "tipo": "egreso", "categoria": "Transporte", "fecha": "2025-07-02"},
    {"id": 4, "usuario_id": 1, "monto": 300, "tipo": "ingreso", "categoria": "Freelance", "fecha": "2025-07-03"},
]

# Modelo de respuesta
class CategoriaTotal(BaseModel):
    categoria: str
    total: float

@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1):
    """
    Devuelve el total por categoría según tipo (ingreso o egreso)
    """
    totales = defaultdict(float)

    for t in transacciones:
        if t["usuario_id"] == usuario_id and t["tipo"] == tipo:
            totales[t["categoria"]] += t["monto"]

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]
