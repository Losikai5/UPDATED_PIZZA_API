from fastapi import FastAPI
from src.auth.routes import auth_router
from src.Orders.routes import Orders_router
from src.Reviews.routes import reviews_router
from src.db.models import User,Orders,Reviews
from src.db.main import init_db
from contextlib import asynccontextmanager
@asynccontextmanager
async def life_span(app:FastAPI):
    print(">>>>starting..........")
    await init_db()
    yield
    print(".........stoping")
version = "v2"
app = FastAPI(title="PIZZA_MANAGEMENT_API",version=version, lifespan=life_span)
app.include_router(auth_router,prefix=f"/api/{version}/auth",tags=["auth"])
app.include_router(Orders_router,prefix=f"/api/{version}/orders",tags=["orders"])
app.include_router(reviews_router,prefix=f"/api/{version}/review",tags=["reviews"])