from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_chief

router = APIRouter(prefix="/cultures", tags=["Культуры"])


@router.get("", response_model=List[schemas.CultureOut])
def list_cultures(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Culture).order_by(models.Culture.name).all()


@router.post("", response_model=schemas.CultureOut, status_code=status.HTTP_201_CREATED)
def create_culture(payload: schemas.CultureCreate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    if db.query(models.Culture).filter(models.Culture.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Такая культура уже есть в справочнике")
    culture = models.Culture(**payload.model_dump())
    db.add(culture)
    db.commit()
    db.refresh(culture)
    return culture


@router.put("/{culture_id}", response_model=schemas.CultureOut)
def update_culture(culture_id: int, payload: schemas.CultureUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    culture = db.query(models.Culture).get(culture_id)
    if not culture:
        raise HTTPException(status_code=404, detail="Культура не найдена")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(culture, field, value)
    db.commit()
    db.refresh(culture)
    return culture


@router.delete("/{culture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_culture(culture_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    culture = db.query(models.Culture).get(culture_id)
    if not culture:
        raise HTTPException(status_code=404, detail="Культура не найдена")
    if db.query(models.Greenhouse).filter(models.Greenhouse.culture_id == culture_id).first():
        raise HTTPException(status_code=400, detail="Культура используется в теплицах, сначала измените их")
    db.delete(culture)
    db.commit()
