from pydantic import BaseModel
from db.models.heroModel import HeroModel

class HeroBase(BaseModel):
    name: str
    age: int | None = None

class HeroPublicDTO(HeroBase):
    id: int

    @staticmethod
    def from_model(heroModel: HeroModel) -> "HeroPublicDTO":
        return HeroPublicDTO(id=heroModel.id, name=heroModel.name, age=heroModel.age)

class HeroCreateDTO(HeroBase):
    secret_name: str

class HeroUpdateDTO(BaseModel):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None