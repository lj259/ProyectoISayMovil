from fastapi import FastAPI
from database import engine, Base
from routes import router

app = FastAPI(title="LanaApp API", version="1.0.0")
app.include_router(router)

Base.metadata.create_all(bind=engine)