import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    chief_agronomist = "chief_agronomist"
    agronomist = "agronomist"


class WorkType(str, enum.Enum):
    sowing = "sowing"
    watering = "watering"
    fertilizing = "fertilizing"
    harvesting = "harvesting"


class ScheduleStatus(str, enum.Enum):
    planned = "planned"
    done = "done"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.agronomist)
    is_active = Column(Boolean, default=True, nullable=False)

    assigned_tasks = relationship("ScheduleTask", back_populates="assignee", foreign_keys="ScheduleTask.assigned_to_id")
    created_tasks = relationship("ScheduleTask", back_populates="creator", foreign_keys="ScheduleTask.created_by_id")
    executions = relationship("WorkExecution", back_populates="executor")


class Culture(Base):
    __tablename__ = "cultures"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    greenhouses = relationship("Greenhouse", back_populates="culture")


class Greenhouse(Base):
    __tablename__ = "greenhouses"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    culture_id = Column(Integer, ForeignKey("cultures.id"), nullable=False)
    area_m2 = Column(Float, nullable=True)

    culture = relationship("Culture", back_populates="greenhouses")
    tasks = relationship("ScheduleTask", back_populates="greenhouse")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    unit = Column(String(20), nullable=False)


class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"

    id = Column(Integer, primary_key=True)
    greenhouse_id = Column(Integer, ForeignKey("greenhouses.id"), nullable=False)
    work_type = Column(Enum(WorkType), nullable=False)
    planned_date = Column(Date, nullable=False)
    status = Column(Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.planned)
    notes = Column(Text, nullable=True)

    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    greenhouse = relationship("Greenhouse", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    execution = relationship("WorkExecution", back_populates="task", uselist=False)


class WorkExecution(Base):
    __tablename__ = "work_executions"

    id = Column(Integer, primary_key=True)
    schedule_task_id = Column(Integer, ForeignKey("schedule_tasks.id"), unique=True, nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actual_date = Column(Date, nullable=False)
    harvest_volume_kg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    task = relationship("ScheduleTask", back_populates="execution")
    executor = relationship("User", back_populates="executions")
    resource_usages = relationship("WorkResourceUsage", back_populates="work_execution", cascade="all, delete-orphan")


class WorkResourceUsage(Base):
    __tablename__ = "work_resource_usages"
    __table_args__ = (UniqueConstraint("work_execution_id", "resource_id", name="uq_execution_resource"),)

    id = Column(Integer, primary_key=True)
    work_execution_id = Column(Integer, ForeignKey("work_executions.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    work_execution = relationship("WorkExecution", back_populates="resource_usages")
    resource = relationship("Resource")
