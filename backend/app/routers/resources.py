from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_chief

router = APIRouter(prefix="/resources", tags=["Ресурсы"])


@router.get("", response_model=List[schemas.ResourceOut])
def list_resources(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Resource).order_by(models.Resource.name).all()


@router.post("", response_model=schemas.ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(payload: schemas.ResourceCreate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    resource = models.Resource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.put("/{resource_id}", response_model=schemas.ResourceOut)
def update_resource(resource_id: int, payload: schemas.ResourceUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    resource = db.query(models.Resource).get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    resource = db.query(models.Resource).get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    if db.query(models.WorkResourceUsage).filter(models.WorkResourceUsage.resource_id == resource_id).first():
        raise HTTPException(status_code=400, detail="Ресурс уже фигурирует в отчётах о выполнении работ")
    db.delete(resource)
    db.commit()
