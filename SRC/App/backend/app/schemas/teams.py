from pydantic import BaseModel


class TeamOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TeamCreateIn(BaseModel):
    name: str