from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/work-executions", tags=["Фактическое выполнение работ"])


def _exec_query(db: Session):
    return db.query(models.WorkExecution).options(
        joinedload(models.WorkExecution.executor),
        joinedload(models.WorkExecution.resource_usages).joinedload(models.WorkResourceUsage.resource),
        joinedload(models.WorkExecution.task).joinedload(models.ScheduleTask.greenhouse).joinedload(models.Greenhouse.culture),
        joinedload(models.WorkExecution.task).joinedload(models.ScheduleTask.assignee),
        joinedload(models.WorkExecution.task).joinedload(models.ScheduleTask.creator),
    )


def _check_permission(task: models.ScheduleTask, current_user: models.User):
    """Вносить факт. выполнение может главный агроном или назначенный исполнитель."""
    is_chief = current_user.role == models.UserRole.chief_agronomist
    is_assignee = task.assigned_to_id == current_user.id
    if not (is_chief or is_assignee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Внести выполнение может только назначенный исполнитель или главный агроном",
        )


@router.get("", response_model=List[schemas.WorkExecutionOut])
def list_executions(
    greenhouse_id: Optional[int] = None,
    culture_id: Optional[int] = None,
    executor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = _exec_query(db).join(models.ScheduleTask)
    if greenhouse_id:
        query = query.filter(models.ScheduleTask.greenhouse_id == greenhouse_id)
    if culture_id:
        query = query.join(models.Greenhouse).filter(models.Greenhouse.culture_id == culture_id)
    if executor_id:
        query = query.filter(models.WorkExecution.executor_id == executor_id)
    return query.order_by(models.WorkExecution.actual_date.desc()).all()


@router.get("/{execution_id}", response_model=schemas.WorkExecutionOut)
def get_execution(execution_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    execution = _exec_query(db).filter(models.WorkExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return execution


@router.post("/tasks/{task_id}", response_model=schemas.WorkExecutionOut, status_code=status.HTTP_201_CREATED)
def create_execution(
    task_id: int,
    payload: schemas.WorkExecutionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Внесение фактического срока выполнения, затраченных ресурсов и объема урожая по задаче графика."""
    task = db.query(models.ScheduleTask).filter(models.ScheduleTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача графика не найдена")
    _check_permission(task, current_user)
    if task.execution is not None:
        raise HTTPException(status_code=400, detail="По этой задаче уже внесено выполнение")

    for r in payload.resources_used:
        if not db.query(models.Resource).filter(models.Resource.id == r.resource_id).first():
            raise HTTPException(status_code=400, detail=f"Ресурс id={r.resource_id} не найден")

    execution = models.WorkExecution(
        schedule_task_id=task.id,
        executor_id=current_user.id,
        actual_date=payload.actual_date,
        harvest_volume_kg=payload.harvest_volume_kg,
        notes=payload.notes,
    )
    db.add(execution)
    db.flush()

    for r in payload.resources_used:
        db.add(models.WorkResourceUsage(work_execution_id=execution.id, resource_id=r.resource_id, quantity=r.quantity))

    task.status = models.ScheduleStatus.done
    db.commit()
    db.refresh(execution)
    return _exec_query(db).filter(models.WorkExecution.id == execution.id).first()


@router.put("/{execution_id}", response_model=schemas.WorkExecutionOut)
def update_execution(
    execution_id: int,
    payload: schemas.WorkExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    execution = db.query(models.WorkExecution).filter(models.WorkExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    _check_permission(execution.task, current_user)

    data = payload.model_dump(exclude_unset=True)
    resources_used = data.pop("resources_used", None)
    for field, value in data.items():
        setattr(execution, field, value)

    if resources_used is not None:
        db.query(models.WorkResourceUsage).filter(models.WorkResourceUsage.work_execution_id == execution.id).delete()
        for r in resources_used:
            if not db.query(models.Resource).filter(models.Resource.id == r["resource_id"]).first():
                raise HTTPException(status_code=400, detail=f"Ресурс id={r['resource_id']} не найден")
            db.add(models.WorkResourceUsage(work_execution_id=execution.id, resource_id=r["resource_id"], quantity=r["quantity"]))

    db.commit()
    db.refresh(execution)
    return _exec_query(db).filter(models.WorkExecution.id == execution.id).first()


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(execution_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    execution = db.query(models.WorkExecution).filter(models.WorkExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    _check_permission(execution.task, current_user)
    task = execution.task
    db.delete(execution)
    task.status = models.ScheduleStatus.planned
    db.commit()
