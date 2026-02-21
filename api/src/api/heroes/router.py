from typing import Annotated
from pydantic import ValidationError
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from db.database import SessionDep
from db.models.heroModel import HeroModel
from api.heroes.schemas import HeroPublicDTO, HeroCreateDTO, HeroUpdateDTO

router = APIRouter(
    prefix="/heroes",
    tags=["heroes"],
    # responses={404: {"description": "Not found"}},
)


# TODO: Refactor to use repository?
@router.post("/")
def create_hero(hero: HeroCreateDTO, session: SessionDep) -> HeroPublicDTO:
    try:
        db_hero = HeroModel.model_validate(hero)
        db_hero.id = None  # Ensure ID is None for new records
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    new_hero = HeroPublicDTO.from_model(db_hero)
    return new_hero

@router.get("/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[HeroPublicDTO]:
    heroes = session.exec(select(HeroModel).offset(offset).limit(limit)).all()
    new_heroes = [HeroPublicDTO.from_model(hero) for hero in heroes]
    return new_heroes

@router.get("/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> HeroPublicDTO:
    hero = session.get(HeroModel, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return HeroPublicDTO.from_model(hero)

@router.patch("/{hero_id}/")
def update_hero(hero_id: int, hero: HeroUpdateDTO, session: SessionDep) -> HeroPublicDTO:
    hero_db = session.get(HeroModel, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return HeroPublicDTO.from_model(hero_db)

@router.delete("/{hero_id}/", status_code=204, responses={204: {"description": "Hero deleted"}})
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(HeroModel, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()