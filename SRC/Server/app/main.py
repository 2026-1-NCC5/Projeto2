import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.db.init_db import init_db
from app.routers.auth import router as auth_router
from app.routers.teams import router as teams_router
from app.routers.readings import router as readings_router
from app.routers.users import router as users_router
from app.routers.goals import router as goals_router
from app.routers.camera_readings import router as camera_readings_router
from app.routers.public import router as public_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Lideranças Empáticas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    for tentativa in range(10):
        try:
            init_db()
            return
        except OperationalError as e:
            if tentativa < 9:
                logger.warning(f"Banco indisponível (tentativa {tentativa + 1}/10), aguardando 3s... {e}")
                time.sleep(3)
            else:
                raise


app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(readings_router)
app.include_router(users_router)
app.include_router(goals_router)
app.include_router(camera_readings_router)
app.include_router(public_router)


@app.get("/")
def root():
    return {"message": "API online"}
