from fastapi import FastAPI
from app.db.base import Base
from app.db.database import engine
from app.models import *
from app.api.route import get_all_router
from fastapi.openapi.utils import get_openapi
from app.middleware.rbacmiddleware import RBACMiddleware

app = FastAPI()
app.include_router(get_all_router())


# Add Bearer token support in Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI with Bearer Auth",
        version="1.0.0",
        description="Paste JWT token using Bearer scheme",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.add_middleware(RBACMiddleware)