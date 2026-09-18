from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_chief

router = APIRouter(prefix="/schedules", tags=["Графики работ"])


def _task_query(db: Session):
    return db.query(models.ScheduleTask).options(
        joinedload(models.ScheduleTask.greenhouse).joinedload(models.Greenhouse.culture),
        joinedload(models.ScheduleTask.assignee),
        joinedload(models.ScheduleTask.creator),
    )


@router.get("", response_model=List[schemas.ScheduleTaskOut])
def list_tasks(
    greenhouse_id: Optional[int] = None,
    culture_id: Optional[int] = None,
    work_type: Optional[models.WorkType] = None,
    status_filter: Optional[models.ScheduleStatus] = None,
    assigned_to_id: Optional[int] = None,
    my_tasks: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Список задач графика с фильтрами. my_tasks=true - только задачи, назначенные текущему пользователю."""
    query = _task_query(db)
    if greenhouse_id:
        query = query.filter(models.ScheduleTask.greenhouse_id == greenhouse_id)
    if culture_id:
        query = query.join(models.Greenhouse).filter(models.Greenhouse.culture_id == culture_id)
    if work_type:
        query = query.filter(models.ScheduleTask.work_type == work_type)
    if status_filter:
        query = query.filter(models.ScheduleTask.status == status_filter)
    if assigned_to_id:
        query = query.filter(models.ScheduleTask.assigned_to_id == assigned_to_id)
    if my_tasks:
        query = query.filter(models.ScheduleTask.assigned_to_id == current_user.id)
    return query.order_by(models.ScheduleTask.planned_date).all()


@router.get("/{task_id}", response_model=schemas.ScheduleTaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    task = _task_query(db).filter(models.ScheduleTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.post("", response_model=schemas.ScheduleTaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.ScheduleTaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_chief)):
    """Составление графика работ - доступно только главному агроному."""
    if not db.query(models.Greenhouse).filter(models.Greenhouse.id == payload.greenhouse_id).first():
        raise HTTPException(status_code=400, detail="Теплица не найдена")
    if payload.assigned_to_id and not db.query(models.User).filter(models.User.id == payload.assigned_to_id).first():
        raise HTTPException(status_code=400, detail="Исполнитель не найден")
    task = models.ScheduleTask(**payload.model_dump(), created_by_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_query(db).filter(models.ScheduleTask.id == task.id).first()


@router.put("/{task_id}", response_model=schemas.ScheduleTaskOut)
def update_task(task_id: int, payload: schemas.ScheduleTaskUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    """Редактирование графика - доступно только главному агроному."""
    task = db.query(models.ScheduleTask).filter(models.ScheduleTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return _task_query(db).filter(models.ScheduleTask.id == task.id).first()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_chief)):
    task = db.query(models.ScheduleTask).filter(models.ScheduleTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
