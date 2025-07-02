from fastapi import FastAPI
from routes. presupuesto_routes import router as presupuesto_router

app = FastAPI(title="API Presupuestos", version="1.0.0")

app.include_router(presupuestos.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)