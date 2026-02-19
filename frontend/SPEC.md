# Todo App Frontend Specification

## Overview
Build a frontend for the Todo API using HTML, CSS (Tailwind CSS), and vanilla JavaScript.

---

## 1. Basic Features Required

### Authentication
- **Login page**: Email + password form
- **Register page**: Email + password form
- **Persistent session**: Store JWT in localStorage
- **Header**: Display logged-in user's email with logout button
- **Protected routes**: Redirect to login if no valid token

### Task Management
- **View tasks**: Display all tasks as cards in a list
- **Create task**: Form with title, description, priority (1-5), due date, tags
- **Edit task**: Update all task fields
- **Delete task**: Remove task with confirmation
- **Toggle completion**: Checkbox to mark complete/incomplete
- **Filtering**: By status (pending/completed), priority, tag, due date range
- **Sorting**: By position, due date, priority, created date

### Tag Management
- **View tags**: List all available tags
- **Create tag**: Name + color picker
- **Delete tag**: Remove tag (with confirmation)
- **Assign tags**: Select multiple tags when creating/editing tasks

---

## 2. UI/Layout Suggestions

### Page Structure

```
┌─────────────────────────────────────────────────────────┐
│ Header: Logo/Title | "Welcome, user@email.com" | Logout │
├─────────────────────────────────────────────────────────┤
│ Toolbar: [+ New Task] [Filter ▼] [Sort ▼]              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task Card                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [☐] Task Title              [Priority: 3] [🗑️] │   │
│  │     Description preview here...                  │   │
│  │     📅 Jan 15, 2025  |  🏷️ Work, Personal        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  (More task cards in vertical list)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Auth Pages (Login/Register)
- Centered card on page
- Email input, password input
- Submit button
- Link to switch between login/register

### Task Card Design
- Checkbox on left for completion toggle
- Title (bold, strikethrough when completed)
- Description preview (truncated)
- Priority badge (color-coded: 1=red, 2=orange, 3=yellow, 4=light-green, 5=green)
- Due date with icon
- Tags as small colored pills
- Edit/Delete buttons on hover or always visible

### Modal Forms
- Overlay with centered modal
- Form fields with labels
- Save/Cancel buttons
- Close on overlay click or X button

### Design Guidelines
- Use **Tailwind CSS** via CDN for styling
- Clean, modern card-based layout
- Color-coded priorities
- Visual distinction: completed tasks (strikethrough, reduced opacity)
- Responsive: single column on mobile, comfortable width on desktop

---

## 3. Development Stages

### Stage 1: Setup
- Create `index.html` (main app), `login.html`, `register.html`
- Link Tailwind CSS via CDN in all pages
- Create `style.css` for custom styles
- Create `app.js` for JavaScript logic

### Stage 2: Authentication UI
- Build login form in `login.html`
- Build register form in `register.html`
- Add basic form validation and error display
- Style with Tailwind

### Stage 3: Authentication Logic
- Implement JWT storage in localStorage
- Create API service functions (login, register, getCurrentUser)
- Handle token expiration and logout
- Create simple router (check token, redirect)

### Stage 4: Task List Display
- Fetch tasks from API on page load
- Render tasks as cards dynamically
- Show loading state while fetching
- Handle empty state (no tasks message)

### Stage 5: Task CRUD Operations
- Create "New Task" button and modal form
- Implement create task API call
- Implement edit task (pre-fill modal, update API call)
- Implement delete task with confirmation dialog
- Implement toggle completion

### Stage 6: Filters, Sorting & Tags
- Add filter dropdown (status, priority, tag)
- Add sort dropdown
- Implement filter/sort API calls
- Add tag management (create, delete, assign to tasks)

### Stage 7: Polish
- Error handling (show user-friendly messages)
- Form validation feedback
- Responsive design check
- Confirm dialogs for destructive actions

---

## 4. API Endpoints Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Get current user info |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List tasks (supports query params) |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get single task |
| PATCH | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| PATCH | `/tasks/{id}/toggle` | Toggle completion |
| PUT | `/tasks/reorder` | Reorder tasks |

### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tags` | List tags |
| POST | `/tags` | Create tag |
| DELETE | `/tags/{id}` | Delete tag |

### Query Parameters for GET /tasks
- `status`: "completed" or "pending"
- `priority`: 1-5
- `tag_id`: tag ID
- `due_before`: ISO datetime
- `due_after`: ISO datetime
- `overdue`: true/false
- `no_due_date`: true/false
- `sort_by`: "position", "due_date", "priority", "created_at"
- `sort_order`: "asc" or "desc"

### Authentication
All protected endpoints require header:
```
Authorization: Bearer <token>
```

---

## 5. File Structure Suggestion

```
todo-frontend/
├── index.html        # Main app (task list)
├── login.html        # Login page
├── register.html     # Register page
├── css/
│   └── style.css     # Custom styles
└── js/
    ├── app.js        # Main application logic
    ├── api.js        # API service functions
    ├── auth.js       # Auth utilities
    └── router.js     # Simple client-side routing
```

---

## 6. Example API Calls

### Login
```javascript
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=email@example.com&password=secret'
});
const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

### Get Tasks (with auth)
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const tasks = await response.json();
```

---

## 7. Acceptance Criteria

- [ ] User can register a new account
- [ ] User can login and logout
- [ ] User sees their own tasks only
- [ ] User can create a new task with all fields
- [ ] User can edit an existing task
- [ ] User can delete a task
- [ ] User can mark task as complete/incomplete
- [ ] User can filter tasks by status, priority, tag
- [ ] User can sort tasks by various fields
- [ ] User can create and delete tags
- [ ] User can assign tags to tasks
- [ ] App works on mobile devices
- [ ] App shows appropriate error messages
