# 📝 Online Examination System

A full-stack Online Examination System built with **FastAPI**, **MySQL**, **Redis**, and a **Vanilla JS** frontend.

## 🏗 Project Structure

```
exam_system/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, DB, Security, Cache, Logger
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── routes/        # API endpoints
│   │   ├── middleware/    # Logging middleware
│   │   ├── tests/         # pytest test suite
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── static/css/style.css
│   ├── static/js/app.js
│   └── nginx.conf
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop + WSL2
- PowerShell or WSL terminal

### Run the Project

```powershell
# Clone / navigate to project
cd exam_system

# Build and start all services
docker-compose up --build

# Access the app:
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/docs
# Backend:   http://localhost:8000
```

### Stop the Project
```powershell
docker-compose down
```

### Reset Database
```powershell
docker-compose down -v   # removes volumes too
docker-compose up --build
```

## 🧪 Run Tests

```powershell
# Run tests inside the backend container
docker-compose exec backend pytest app/tests/ -v
```

## 👥 Roles

| Role    | Permissions |
|---------|-------------|
| Admin   | Create/Edit/Delete exams, view all results, analytics, monitoring |
| Student | Take exams, view own results |

## 🔑 API Endpoints

### Auth
- `POST /api/auth/register` - Register (admin or student)
- `POST /api/auth/login` - Login → returns JWT
- `GET  /api/auth/me` - Get current user

### Exams (Admin only for write)
- `GET    /api/exams/` - List all active exams
- `POST   /api/exams/` - Create exam with questions (**Admin**)
- `GET    /api/exams/{id}` - Get exam detail
- `PUT    /api/exams/{id}` - Update exam (**Admin**)
- `DELETE /api/exams/{id}` - Delete exam (**Admin**)

### Results
- `POST /api/results/submit` - Submit exam answers
- `GET  /api/results/my` - Student's own results
- `GET  /api/results/my/{id}` - Result detail
- `GET  /api/results/admin/all` - All results (**Admin**)
- `GET  /api/results/analytics/{exam_id}` - Exam analytics (**Admin**)

### Monitoring
- `GET /api/monitoring/health` - Health check
- `GET /api/monitoring/stats` - System stats (**Admin**)
- `GET /api/monitoring/logs` - Recent logs (**Admin**)

## ⚙️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PyMySQL, Pydantic v2
- **Auth:** JWT (python-jose), bcrypt (passlib)
- **Cache:** Redis (Cache-Aside Pattern)
- **Logging:** Loguru
- **Testing:** pytest, FastAPI TestClient
- **Database:** MySQL 8.0
- **Frontend:** HTML/CSS/Vanilla JS
- **Proxy:** Nginx
- **Containerization:** Docker + docker-compose
