from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Tienda API",
    description="Backend serverless para tienda con módulos clientes, ventas, compras e inventario",
    version="1.0.0",
    lifespan=lifespan
)

from app.modules.clientes.router import router as clientes_router
from app.modules.ventas.router import router as ventas_router
from app.modules.compra.router import router as compra_router
from app.modules.inventario.router import router as inventario_router

app.include_router(clientes_router)
app.include_router(ventas_router)
app.include_router(compra_router)
app.include_router(inventario_router)


@app.get("/")
async def root():
    return {"message": "Tienda API - Backend serverless"}

@app.get("/health")
async def health():
    return {"status": "healthy"}