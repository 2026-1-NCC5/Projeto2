from app.db.database import Base, engine
from app.db.base import *  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)