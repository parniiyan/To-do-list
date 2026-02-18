from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tag, User
from app.schemas import TagCreate, TagResponse
from app.auth import get_current_user_optional

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagResponse])
def get_tags(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if current_user:
        return db.query(Tag).filter((Tag.user_id == current_user.id) | (Tag.user_id == None)).all()
    return db.query(Tag).filter(Tag.user_id == None).all()


@router.post("", response_model=TagResponse, status_code=201)
def create_tag(
    tag: TagCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    db_tag = Tag(name=tag.name, color=tag.color, user_id=current_user.id if current_user else None)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if current_user and tag.user_id not in (current_user.id, None):
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user and tag.user_id is not None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()
    return None
