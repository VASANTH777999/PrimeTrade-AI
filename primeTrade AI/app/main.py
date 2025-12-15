from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import User, Task
from app.schemas import UserCreate, UserLogin, UserOut, Token, TaskCreate, TaskUpdate, TaskOut
from app.auth import create_access_token, get_current_user, require_admin
from app.crud import get_user_by_email, create_user, authenticate, create_task, list_tasks_for_user, list_tasks_all, get_task, update_task, delete_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PrimeTrade AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/login")
def serve_login():
    return FileResponse("static/login.html")

@app.get("/register")
def serve_register():
    return FileResponse("static/register.html")

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/meta.json")
def app_meta():
    return {
        "name": "PrimeTrade AI",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": ["/", "/login", "/register", "/dashboard"],
        "api_base": "/api/v1",
    }
@app.post("/api/v1/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = create_user(db, payload.email, payload.password)
    return UserOut(id=user.id, email=user.email, role=user.role, created_at=user.created_at.isoformat() if user.created_at else None)

@app.post("/api/v1/auth/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return Token(access_token=token, token_type="bearer")

@app.get("/api/v1/users", response_model=list[UserOut])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserOut(id=u.id, email=u.email, role=u.role, created_at=u.created_at.isoformat() if u.created_at else None) for u in users]

@app.get("/api/v1/tasks", response_model=list[TaskOut])
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), all: bool = False):
    items = list_tasks_all(db) if (all and current_user.role == "admin") else list_tasks_for_user(db, current_user.id)
    return [TaskOut(id=t.id, title=t.title, description=t.description, status=t.status, owner_id=t.owner_id, created_at=t.created_at.isoformat() if t.created_at else None, updated_at=t.updated_at.isoformat() if t.updated_at else None) for t in items]

@app.post("/api/v1/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(payload: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = create_task(db, current_user.id, payload.title, payload.description)
    return TaskOut(id=t.id, title=t.title, description=t.description, status=t.status, owner_id=t.owner_id, created_at=t.created_at.isoformat() if t.created_at else None, updated_at=t.updated_at.isoformat() if t.updated_at else None)

@app.get("/api/v1/tasks/{task_id}", response_model=TaskOut)
def get_task_endpoint(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = get_task(db, task_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role != "admin" and t.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return TaskOut(id=t.id, title=t.title, description=t.description, status=t.status, owner_id=t.owner_id, created_at=t.created_at.isoformat() if t.created_at else None, updated_at=t.updated_at.isoformat() if t.updated_at else None)

@app.put("/api/v1/tasks/{task_id}", response_model=TaskOut)
def update_task_endpoint(task_id: int, payload: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = get_task(db, task_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role != "admin" and t.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    t = update_task(db, t, payload.title, payload.description, payload.status)
    return TaskOut(id=t.id, title=t.title, description=t.description, status=t.status, owner_id=t.owner_id, created_at=t.created_at.isoformat() if t.created_at else None, updated_at=t.updated_at.isoformat() if t.updated_at else None)

@app.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = get_task(db, task_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role != "admin" and t.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_task(db, t)
    return
