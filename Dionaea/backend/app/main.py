from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.data import router as data_router
from app.api.v1.roles import router as roles_router
from app.core.config import settings
from app.db.database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(roles_router, prefix=f"{settings.API_V1_STR}/roles", tags=["roles"])
app.include_router(data_router, prefix=f"{settings.API_V1_STR}/data", tags=["data"])

@app.get("/")
def read_root():
    return {"message": "Dionaea Log Manager API is running"}
