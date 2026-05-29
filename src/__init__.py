from fastapi import FastAPI
from src.auth.routes import auth_router
from src.Orders.routes import Orders_router
from src.Reviews.routes import reviews_router
from src.Admin.routes import admin_router
from src.notifications.routes import notification_router
from src.middleware import register_middleware
from src.Menu.routes import menu_router
from src.Cart.routes import cart_router
from src.Addresse.routes import address_router


version = "v2"
app = FastAPI(title="PIZZA_MANAGEMENT_API",version=version, contact={"name": "Losika","email": "losikanicholasi5@gmail.com",})
register_middleware(app)
app.include_router(auth_router,prefix=f"/api/{version}/auth",tags=["auth"])
app.include_router(Orders_router,prefix=f"/api/{version}/orders",tags=["orders"])
app.include_router(reviews_router,prefix=f"/api/{version}/review",tags=["reviews"])
app.include_router(admin_router,prefix=f"/api/{version}/admin",tags=["admin"])
app.include_router(notification_router,prefix=f"/api/{version}/notifications",tags=["notifications"])
app.include_router(menu_router,prefix=f"/api/{version}/menu",tags=["menu"])
app.include_router(cart_router,prefix=f"/api/{version}/cart",tags=["cart"])
app.include_router(address_router,prefix=f"/api/{version}/addresses",tags=["addresses"])