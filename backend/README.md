# Todo Backend

FastAPI backend for Todo List Application with SQLite.

## Setup

```bash
cd backend
uv sync
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## API Documentation

Interactive docs available at `http://localhost:8000/docs`

---

## Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create new account |
| `POST` | `/auth/login` | Login and get JWT token |
| `GET` | `/auth/me` | Get current user info |

#### Register (POST /auth/register)

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-18T10:00:00"
}
```

#### Login (POST /auth/login)

Uses OAuth2 password flow - send as form data:

```
email=user@example.com&password=yourpassword
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User (GET /auth/me)

Requires Bearer token in Authorization header:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-18T10:00:00"
}
```

---

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tasks` | List all tasks |
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks/{id}` | Get a specific task |
| `PATCH` | `/tasks/{id}` | Partial update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `PATCH` | `/tasks/{id}/toggle` | Toggle task completion |
| `PUT` | `/tasks/reorder` | Bulk reorder tasks |

#### Task Filters (GET /tasks)

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter: `completed`, `pending` |
| `priority` | string | Filter: `low`, `medium`, `high` |
| `tag_id` | int | Filter by tag |
| `due_before` | datetime | Due before date |
| `due_after` | datetime | Due after date |
| `overdue` | bool | Show only overdue pending |
| `no_due_date` | bool | Show tasks without due date |
| `sort_by` | string | Sort: `position`, `due_date`, `priority`, `created_at` |
| `sort_order` | string | Direction: `asc`, `desc` |

#### Task Object

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Optional description",
  "completed": false,
  "priority": "medium",
  "due_date": "2026-02-20T10:00:00",
  "position": 1.0,
  "user_id": null,
  "created_at": "2026-02-18T10:00:00",
  "updated_at": "2026-02-18T10:00:00",
  "tags": []
}
```

#### Create Task (POST /tasks)

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2026-02-20T10:00:00",
  "tag_ids": [1, 2]
}
```

#### Update Task (PATCH /tasks/{id})

```json
{
  "title": "Updated title",
  "completed": true,
  "priority": "low",
  "tag_ids": [1]
}
```

#### Reorder Tasks (PUT /tasks/reorder)

```json
{
  "tasks": [
    {"id": 1, "position": 1.0},
    {"id": 2, "position": 2.0},
    {"id": 3, "position": 1.5}
  ]
}
```

---

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tags` | List all tags |
| `POST` | `/tags` | Create a new tag |
| `DELETE` | `/tags/{id}` | Delete a tag |

#### Tag Object

```json
{
  "id": 1,
  "name": "work",
  "color": "#ff0000",
  "created_at": "2026-02-18T10:00:00"
}
```

#### Create Tag (POST /tags)

```json
{
  "name": "work",
  "color": "#ff0000"
}
```

---

## Frontend Requirements

### Stage 1: Core Task Management
- Display all tasks in a list
- Create new task (title required, optional description/priority/due_date)
- Edit existing task
- Delete task
- Toggle task completion

### Stage 2: Filtering & Sorting
- Filter by: completed/pending
- Filter by priority
- Sort by: position, due date, priority, creation date

### Stage 3: Tags
- Display tags
- Create/delete tags
- Assign tags to tasks
- Filter tasks by tag

### Stage 4: Drag & Drop
- Reorder tasks via drag and drop
- Persist order to backend

### Stage 5: Authentication
- User registration
- User login (JWT)
- Private tasks per user
- Associate tasks/tags with logged-in user

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── database.py       # SQLite config
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # Auth utilities
│   └── routers/
│       ├── auth.py       # Auth endpoints
│       ├── tasks.py      # Task endpoints
│       └── tags.py       # Tag endpoints
├── pyproject.toml
└── todo.db               # SQLite database (created on first run)
```

---

## Authentication Notes

- Tasks/tags without `user_id` are public (backward compatible)
- When logged in, you see your tasks + public tasks
- Created tasks are associated with the logged-in user
- Use `Authorization: Bearer <token>` header for authenticated requests
