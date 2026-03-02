from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.teams import router as teams_router
from app.routers.readings import router as readings_router
from app.routers.goals import router as goals_router

app = FastAPI(title=settings.APP_NAME)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")] if settings.ALLOWED_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(readings_router)
app.include_router(goals_router)


@app.get("/health")
def health():
    return {"ok": True, "env": settings.ENV}