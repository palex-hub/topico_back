from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Store API",
    description="Serverless backend for store with modules: customers, sales, purchases and inventory",
    version="1.0.0",
    lifespan=lifespan
)

from app.modules.customers.router import router as customers_router
from app.modules.sales.router import router as sales_router
from app.modules.purchase.router import router as purchases_router
from app.modules.inventory.router import router as inventory_router

app.include_router(customers_router)
app.include_router(sales_router)
app.include_router(purchases_router)
app.include_router(inventory_router)


@app.get("/")
async def root():
    return {"message": "Store API - Serverless backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
