from fastapi import FastAPI
from app.database import engine, Base

# IMPORTANTE: Debes importar tus modelos aquí para que SQLAlquemy los registre
# Ejemplo si tienes módulos de 'usuarios' e 'inventario':
# from app.modules.usuarios.models.user import User
# from app.modules.inventario.models.producto import Producto

from app.modules.ventas.router import router as ventas_router
# from app.modules.inventario.router import router as inventario_router

# Crea las tablas en Postgres (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mi API con Postgres",
    description="Estructura modular con FastAPI y SQLAlchemy",
    version="1.0.0"
)

# Registro de rutas de los módulos
app.include_router(ventas_router)
# app.include_router(inventario_router)

@app.get("/")
async def root():
    return {"message": "API conectada a PostgreSQL exitosamente"}