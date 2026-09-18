from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import ScheduleStatus, UserRole, WorkType


# --- auth ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- users ---

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.agronomist


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


# --- cultures ---

class CultureBase(BaseModel):
    name: str
    description: Optional[str] = None


class CultureCreate(CultureBase):
    pass


class CultureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CultureOut(CultureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# --- greenhouses ---

class GreenhouseBase(BaseModel):
    name: str
    culture_id: int
    area_m2: Optional[float] = None


class GreenhouseCreate(GreenhouseBase):
    pass


class GreenhouseUpdate(BaseModel):
    name: Optional[str] = None
    culture_id: Optional[int] = None
    area_m2: Optional[float] = None


class GreenhouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    culture_id: int
    area_m2: Optional[float] = None
    culture: CultureOut


# --- resources ---

class ResourceBase(BaseModel):
    name: str
    unit: str


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# --- schedule tasks ---

class ScheduleTaskCreate(BaseModel):
    greenhouse_id: int
    work_type: WorkType
    planned_date: date
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None


class ScheduleTaskUpdate(BaseModel):
    work_type: Optional[WorkType] = None
    planned_date: Optional[date] = None
    status: Optional[ScheduleStatus] = None
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None


class ScheduleTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    greenhouse_id: int
    work_type: WorkType
    planned_date: date
    status: ScheduleStatus
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    created_by_id: int

    greenhouse: GreenhouseOut
    assignee: Optional[UserOut] = None
    creator: UserOut


# --- work executions ---

class ResourceUsageIn(BaseModel):
    resource_id: int
    quantity: float


class ResourceUsageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource_id: int
    quantity: float
    resource: ResourceOut


class WorkExecutionCreate(BaseModel):
    actual_date: date
    harvest_volume_kg: Optional[float] = None
    notes: Optional[str] = None
    resources_used: list[ResourceUsageIn] = []


class WorkExecutionUpdate(BaseModel):
    actual_date: Optional[date] = None
    harvest_volume_kg: Optional[float] = None
    notes: Optional[str] = None
    resources_used: Optional[list[ResourceUsageIn]] = None


class WorkExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    schedule_task_id: int
    executor_id: int
    actual_date: date
    harvest_volume_kg: Optional[float] = None
    notes: Optional[str] = None

    task: ScheduleTaskOut
    executor: UserOut
    resource_usages: list[ResourceUsageOut] = []
