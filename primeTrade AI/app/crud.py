from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User, Task
from app.auth import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

def create_user(db: Session, email: str, password: str) -> User:
    user = User(email=email, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_task(db: Session, owner_id: int, title: str, description: str | None):
    task = Task(title=title, description=description, owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def list_tasks_for_user(db: Session, owner_id: int):
    return db.execute(select(Task).where(Task.owner_id == owner_id)).scalars().all()

def list_tasks_all(db: Session):
    return db.execute(select(Task)).scalars().all()

def get_task(db: Session, task_id: int) -> Task | None:
    return db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

def update_task(db: Session, task: Task, title: str | None, description: str | None, status: str | None):
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: Task):
    db.delete(task)
    db.commit()
