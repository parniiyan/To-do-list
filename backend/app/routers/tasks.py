from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.database import get_db
from app.models import Task, Tag, User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, ReorderRequest
from app.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = Query(None, description="Filter by completed or pending"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority: 1-5"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    due_before: Optional[datetime] = Query(None, description="Due before date"),
    due_after: Optional[datetime] = Query(None, description="Due after date"),
    overdue: Optional[bool] = Query(None, description="Show only overdue pending tasks"),
    no_due_date: Optional[bool] = Query(None, description="Show tasks without due date"),
    sort_by: Optional[str] = Query("position", description="Sort by: position, due_date, priority, created_at"),
    sort_order: Optional[str] = Query("asc", description="Sort direction: asc, desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status == "completed":
        query = query.filter(Task.completed == True)
    elif status == "pending":
        query = query.filter(Task.completed == False)

    if priority:
        query = query.filter(Task.priority == priority)

    if tag_id:
        query = query.filter(Task.tags.any(Tag.id == tag_id))

    if due_before:
        query = query.filter(Task.due_date <= due_before)

    if due_after:
        query = query.filter(Task.due_date >= due_after)

    if overdue:
        query = query.filter(
            Task.completed == False,
            Task.due_date < datetime.now()
        )

    if no_due_date:
        query = query.filter(Task.due_date == None)

    sort_column = getattr(Task, sort_by, Task.position)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    return query.all()


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        user_id=current_user.id,
    )

    if task.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(task.tag_ids)).all()
        db_task.tags = tags

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)

    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            task.tags = tags

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    db.commit()
    db.refresh(task)
    return task


@router.put("/reorder", status_code=204)
def reorder_tasks(
    reorder: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for item in reorder.tasks:
        task = db.query(Task).filter(Task.id == item.id).first()
        if task and task.user_id == current_user.id:
            task.position = item.position

    db.commit()
    return None
