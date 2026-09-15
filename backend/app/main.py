from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.documents import router as documents_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "KYC Platform API is running"
    }


app.include_router(health_router)
app.include_router(users_router)
app.include_router(documents_router)