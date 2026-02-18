# AGENTS.md - Backend Development Guidelines

This document provides guidelines for agents working on the Todo Backend codebase.

---

## 1. Build, Run, and Test Commands

### Virtual Environment
```bash
cd To-do-list/backend
source .venv/bin/activate  # or use .venv/bin/python
```

### Install Dependencies
```bash
uv sync          # Install all dependencies
uv sync --dev    # Install dev dependencies
```

### Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
# All tests
pytest tests/

# Single test file
pytest tests/test_auth.py

# Single test
pytest tests/test_auth.py::TestAuthRegistration::test_register_new_user

# With verbose output
pytest tests/ -v

# Run tests matching a pattern
pytest tests/ -k "test_create"
```

### Code Quality (if configured)
```bash
# Ruff linter (if added)
ruff check .

# Black formatter (if added)
black .

# MyPy type checker (if added)
mypy .
```

---

## 2. Code Style Guidelines

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # SQLAlchemy database config
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # Authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── tasks.py      # Task endpoints
│       ├── tags.py       # Tag endpoints
│       └── auth.py       # Auth endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   ├── test_auth.py
│   ├── test_tasks.py
│   ├── test_tags.py
│   └── test_*.py
├── pyproject.toml
└── README.md
```

### Python Version
- Minimum Python 3.10
- Currently using Python 3.12

### Imports
- Standard library imports first
- Third-party imports second
- Local application imports third
- Separate each group with a blank line
- Use absolute imports (e.g., `from app.models import Task`)

Example:
```python
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Tag
from app.schemas import TaskCreate, TaskResponse
```

### Naming Conventions
- **Files**: snake_case (e.g., `task_routes.py`)
- **Classes**: PascalCase (e.g., `class TaskResponse`)
- **Functions/variables**: snake_case (e.g., `def get_tasks()`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `SECRET_KEY`)
- **Database tables**: singular, lowercase (e.g., `tasks`, `users`)

### Type Hints
- Use type hints for all function parameters and return types
- Use `Optional[X]` instead of `X | None` for compatibility
- Use `List[X]` from typing for compatibility

```python
def get_tasks(
    status: Optional[str] = None,
    priority: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
```

### Pydantic Schemas
- Use `BaseModel` for request/response schemas
- Use `ConfigDict(from_attributes=True)` for response models
- Use `Field()` for validation constraints

```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tag_ids: List[int] = []

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    
    model_config = ConfigDict(from_attributes=True)
```

### SQLAlchemy Models
- Use declarative base pattern
- Define relationships using `relationship()`
- Use appropriate column types (Integer, String, Boolean, DateTime, Float)
- Always include `primary_key=True` on ID columns

```python
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="tasks")
```

### Error Handling
- Use HTTPException for API errors with appropriate status codes
- Return 404 for not found, 400 for bad request, 401 for unauthorized
- Include descriptive error messages

```python
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### API Endpoint Conventions
- Use RESTful patterns: GET/POST/PATCH/DELETE
- Use plural nouns for collections: `/tasks`, `/tags`
- Use query parameters for filtering: `/tasks?status=completed`
- Return appropriate status codes:
  - 200 OK
  - 201 Created
  - 204 No Content
  - 400 Bad Request
  - 401 Unauthorized
  - 404 Not Found
  - 422 Unprocessable Entity

### Authentication
- Use JWT tokens with python-jose
- Passwords hashed with bcrypt
- Token passed via Authorization header: `Bearer <token>`
- Use dependency injection for auth

```python
from app.auth import get_current_user, get_current_user_optional

# Required auth
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user}

# Optional auth
@router.get("/tasks")
def get_tasks(current_user: Optional[User] = Depends(get_current_user_optional)):
    # Handle both authenticated and anonymous users
```

### Testing Conventions
- Use pytest with fixtures
- Use in-memory SQLite for tests
- Override database dependency in tests
- Use descriptive test names: `test_<method>_<expected_behavior>`

```python
@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### Database
- SQLite for development (sqlite:///:memory: for tests)
- Use migrations for production (Alembic not currently configured)
- Foreign keys must be explicitly defined

---

## 3. Key Files Reference

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization, router registration |
| `app/database.py` | SQLAlchemy engine, session, base configuration |
| `app/models.py` | ORM models (User, Task, Tag) |
| `app/schemas.py` | Pydantic models for request/response validation |
| `app/auth.py` | Password hashing, JWT creation/verification, auth dependencies |
| `app/routers/tasks.py` | Task CRUD endpoints, filtering, sorting |
| `app/routers/tags.py` | Tag CRUD endpoints |
| `app/routers/auth.py` | Registration, login, current user endpoints |
| `tests/conftest.py` | Pytest fixtures for testing |

---

## 4. Common Patterns

### Creating a New Endpoint
1. Add schema to `app/schemas.py` if needed
2. Add route to appropriate router in `app/routers/`
3. Register router in `app/main.py`
4. Add tests to `tests/`

### Adding a New Model
1. Add model class to `app/models.py`
2. Add Pydantic schemas to `app/schemas.py`
3. Run `Base.metadata.create_all(bind=engine)` or restart server

### Running Specific Tests
```bash
# By file
pytest tests/test_tasks.py -v

# By class
pytest tests/test_tasks.py::TestTaskCreate -v

# By function name
pytest tests/test_tasks.py::TestTaskCreate::test_create_task_with_auth -v
```
