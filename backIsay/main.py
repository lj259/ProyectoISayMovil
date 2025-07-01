from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

app = FastAPI()

# Simulamos una "base de datos"
transacciones = [
    {"id": 1, "usuario_id": 1, "monto": 1000, "tipo": "ingreso", "categoria": "Sueldo", "fecha": "2025-01-10"},
    {"id": 2, "usuario_id": 1, "monto": 500, "tipo": "egreso", "categoria": "Comida", "fecha": "2025-01-15"},
    {"id": 3, "usuario_id": 1, "monto": 200, "tipo": "egreso", "categoria": "Transporte", "fecha": "2025-02-01"},
    {"id": 4, "usuario_id": 1, "monto": 300, "tipo": "ingreso", "categoria": "Freelance", "fecha": "2025-02-03"},
    {"id": 5, "usuario_id": 1, "monto": 100, "tipo": "ahorro", "categoria": "Banco", "fecha": "2025-03-05"},
    {"id": 6, "usuario_id": 1, "monto": 400, "tipo": "ahorro", "categoria": "Banco", "fecha": "2025-03-20"},
]


MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# 1. Endpoint: Distribución por categoría (gráfico circular)
class CategoriaTotal(BaseModel):
    categoria: str
    total: float

@app.get("/graficas/categorias", response_model=List[CategoriaTotal])
def graficas_por_categoria(tipo: str, usuario_id: int = 1):
    """
    Devuelve el total por categoría según tipo (ingreso, egreso o ahorro)
    """
    totales = defaultdict(float)

    for t in transacciones:
        if t["usuario_id"] == usuario_id and t["tipo"] == tipo:
            totales[t["categoria"]] += t["monto"]

    return [{"categoria": cat, "total": total} for cat, total in totales.items()]

# 2. Endpoint: Tendencia mensual (gráfico de barras)
class TendenciaMensual(BaseModel):
    mes: str
    total: float

@app.get("/graficas/tendencias", response_model=List[TendenciaMensual])
def tendencias_mensuales(tipo: str, usuario_id: int = 1):
    """
    Devuelve la suma mensual de transacciones por tipo (ingreso, egreso o ahorro)
    """
    totales_por_mes = defaultdict(float)

    for t in transacciones:
        if t["usuario_id"] == usuario_id and t["tipo"] == tipo:
            fecha = datetime.strptime(t["fecha"], "%Y-%m-%d")
            mes = fecha.month
            totales_por_mes[mes] += t["monto"]

    return [
        {"mes": MESES_ES[mes], "total": totales_por_mes[mes]}
        for mes in sorted(totales_por_mes.keys())
    ]