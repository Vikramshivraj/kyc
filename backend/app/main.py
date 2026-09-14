from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.users import router as users_router


app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "KYC Platform API is running"
    }


app.include_router(health_router)
app.include_router(users_router)