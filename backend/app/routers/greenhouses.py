from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_chief

router = APIRouter(prefix="/greenhouses", tags=["Теплицы"])


def _query(db: Session):
    return db.query(models.Greenhouse).options(joinedload(models.Greenhouse.culture))


@router.get("", response_model=List[schemas.GreenhouseOut])
def list_greenhouses(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return _query(db).order_by(models.Greenhouse.name).all()


@router.post("", response_model=schemas.GreenhouseOut, status_code=status.HTTP_201_CREATED)
def create_greenhouse(payload: schemas.GreenhouseCreate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    if not db.query(models.Culture).get(payload.culture_id):
        raise HTTPException(status_code=400, detail="Культура не найдена")
    greenhouse = models.Greenhouse(**payload.model_dump())
    db.add(greenhouse)
    db.commit()
    db.refresh(greenhouse)
    return _query(db).filter(models.Greenhouse.id == greenhouse.id).first()


@router.put("/{greenhouse_id}", response_model=schemas.GreenhouseOut)
def update_greenhouse(greenhouse_id: int, payload: schemas.GreenhouseUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    greenhouse = db.query(models.Greenhouse).get(greenhouse_id)
    if not greenhouse:
        raise HTTPException(status_code=404, detail="Теплица не найдена")
    data = payload.model_dump(exclude_unset=True)
    if "culture_id" in data and not db.query(models.Culture).get(data["culture_id"]):
        raise HTTPException(status_code=400, detail="Культура не найдена")
    for field, value in data.items():
        setattr(greenhouse, field, value)
    db.commit()
    db.refresh(greenhouse)
    return _query(db).filter(models.Greenhouse.id == greenhouse.id).first()


@router.delete("/{greenhouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_greenhouse(greenhouse_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    greenhouse = db.query(models.Greenhouse).get(greenhouse_id)
    if not greenhouse:
        raise HTTPException(status_code=404, detail="Теплица не найдена")
    if db.query(models.ScheduleTask).filter(models.ScheduleTask.greenhouse_id == greenhouse_id).first():
        raise HTTPException(status_code=400, detail="По теплице есть задачи в графике работ, удалить нельзя")
    db.delete(greenhouse)
    db.commit()
