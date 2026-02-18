from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str
    color: str = "#6b7280"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    user_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    tag_ids: List[int] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None
    position: Optional[float] = None
    tag_ids: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    completed: bool
    position: float
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ReorderItem(BaseModel):
    id: int
    position: float


class ReorderRequest(BaseModel):
    tasks: List[ReorderItem]


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
