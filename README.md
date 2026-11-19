# CampusConnect — College Event Management System

> **Your Campus. Your Community.**  
> *A full-stack, web-based college event management platform built using Python, Flask, Jinja2, and MySQL 8.*

Designed specifically for academic project evaluations, live lab demonstrations, technical viva examinations, and software developer portfolios.

---

## 📌 Project Overview

College campuses frequently struggle with fragmented event communication. Announcements, schedules, venue details, and registration forms are scattered across paper notice boards, WhatsApp groups, and unstructured spreadsheets.

**CampusConnect** solves this challenge by providing a centralized platform where:
- **Students** can discover upcoming hackathons, cultural festivals, sports tournaments, workshops, and guest seminars, register with a single click, monitor seat availability in real time, and manage or cancel their bookings.
- **Administrators** can create, update, and manage college events, track real-time venue capacity and occupancy rates, access student participant rosters, and prevent overbooking.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Primary Language** | **Python 3.12+** (tested on Python 3.13) | Clean, readable, robust language suitable for modern backend development. |
| **Web Framework** | **Flask** | Lightweight, modular Python microframework utilizing the Application Factory Pattern. |
| **Database** | **MySQL 8** (with SQLite fallback) | Production-grade relational database with ACID transactions, indexing, and foreign keys. |
| **ORM** | **Flask-SQLAlchemy** | Pythonic Object-Relational Mapping with cascading deletes and relationship querying. |
| **Database Migrations** | **Flask-Migrate / Alembic** | Tracks and applies database schema migrations safely. |
| **Authentication** | **Flask-Login** | Session-based authentication, user loader hooks, and protected route handlers. |
| **Password Hashing** | **Werkzeug** | Salted SHA-256 / PBKDF2 one-way password hashing (never plaintext). |
| **Forms & CSRF** | **Flask-WTF & WTForms** | Server-side form validation, sanitized input fields, and CSRF token verification. |
| **Environment Config**| **python-dotenv** | Securely loads credentials and runtime variables from `.env`. |
| **Testing Suite** | **pytest** | Automated test suite with test client fixtures and isolated in-memory SQLite database. |
| **Frontend Styling** | **Vanilla CSS3 & Jinja2** | Custom, responsive design system with a tailored color palette and smooth micro-animations. |

---

## 🎨 Design System & Color Palette

CampusConnect uses an intentional, high-contrast, modern collegiate palette:
- **Deep Purple** (`#37306B`): Primary brand color, headers, navigation.
- **Teal** (`#2A9D8F`): Accent buttons, active highlights, success badges.
- **Light Cream** (`#FAF9F6`): Neutral background color for reduced eye strain.
- **Warm Yellow** (`#F4C95D`): Spotlight tags, warning alerts, admin badges.
- **Pure White** (`#FFFFFF`): Elevated card and container surfaces.
- **Typography**: Google Fonts (*Outfit* for bold headings, *Inter* for legible body content).

---

## 📂 Project Architecture & Directory Structure

```text
cc/
├── app/
│   ├── __init__.py           # Application Factory, error handlers, and custom CLI commands
│   ├── extensions.py         # Extension initialization (SQLAlchemy, Migrate, LoginManager, CSRF)
│   ├── models.py             # User, Event, and Registration database models
│   ├── forms.py              # WTForms classes (Signup, Login, EventForm, EmptyForm)
│   ├── auth/                 # Student and Admin authentication blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # /signup, /login, /logout
│   ├── main/                 # Public pages blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # / (homepage with stats & featured events), /about
│   ├── events/               # Event browsing, details, and registration blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # /events, /events/<id>, /events/<id>/register, /events/<id>/cancel
│   ├── student/              # Student dashboard & registration management blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # /student/dashboard, /student/registrations
│   ├── admin/                # Administrator management console blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # /admin/dashboard, create/edit/delete event, participant rosters
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Master layout with responsive navbar, alerts, modal, footer
│   │   ├── home.html         # Landing page with hero, live counters, and category pills
│   │   ├── about.html        # System overview and college viva reference
│   │   ├── signup.html       # Student account registration
│   │   ├── login.html        # Student and Admin login
│   │   ├── events.html       # Searchable and filterable events directory
│   │   ├── event_detail.html # Event details, live capacity bar, and register/cancel actions
│   │   ├── student_dashboard.html # Student hub with active bookings and statistics
│   │   ├── my_registrations.html  # Student registration history with cancellation controls
│   │   ├── admin_dashboard.html   # Admin console with capacity analytics and master event roster
│   │   ├── create_event.html # Admin event scheduling form
│   │   ├── edit_event.html   # Admin event modification form with capacity guard
│   │   ├── event_participants.html # Registered student roster per event
│   │   └── errors/
│   │       ├── 403.html      # Access Denied / Forbidden
│   │       ├── 404.html      # Resource Not Found
│   │       └── 500.html      # Internal Server Error
│   └── static/
│       ├── css/
│       │   └── style.css     # CSS custom properties, grid layouts, cards, and UI components
│       └── js/
│           └── main.js       # Mobile navigation toggle, toast dismissals, and confirmation modals
├── tests/                    # Automated Pytest Suite
│   ├── __init__.py
│   ├── conftest.py           # In-memory test database, client, and user/event fixtures
│   ├── test_auth.py          # Authentication, password hashing, and role security tests
│   ├── test_events.py        # Event browsing, category filters, and admin CRUD tests
│   └── test_registrations.py # Booking constraints, capacity limits, and cancellations tests
├── config.py                 # Application configuration profiles (Dev, Test, Prod)
├── run.py                    # Server launch script & CLI entry point
├── requirements.txt          # Python dependency specifications
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
├── .gitignore                # Git ignore patterns for Python, venvs, and secrets
└── README.md                 # Complete documentation and viva guide
```

---

## 🚀 Setup & Execution Guide (Windows PowerShell)

Follow these exact steps in your Windows terminal:

### 1. Clone or Open the Project
```powershell
cd "c:\Users\AYAN GAMING\cc"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> *Tip: If PowerShell displays an `Execution_Policies` script error, run:*  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### 3. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` (or customize the existing `.env` file):
```powershell
Copy-Item .env.example .env
```

Open `.env` and set your local MySQL root password:
```ini
SECRET_KEY=campusconnect-secret-key-super-secure-2026-viva-demo
DB_HOST=localhost
DB_PORT=3306
DB_NAME=campusconnect
DB_USERNAME=root
DB_PASSWORD=your_actual_mysql_password_here

# When set to True, the application seamlessly falls back to a local SQLite database
# if MySQL credentials are not yet configured or if the MySQL service is offline.
ALLOW_SQLITE_FALLBACK=True

FLASK_ENV=development
FLASK_DEBUG=1
```

### 5. MySQL Database Setup
In MySQL Workbench or the MySQL Command Line Client, execute:
```sql
CREATE DATABASE IF NOT EXISTS campusconnect;
```

### 6. Seed Sample Events and Admin Account
Run the development CLI command to populate sample events (College Hackathon, Cultural Fest, Sports Meet, Web Dev Workshop, Technical Seminar):
```powershell
python run.py seed-events
```
> **Default Admin Credentials Generated:**
> - **Email:** `admin@campusconnect.edu`
> - **Password:** `Admin@123`

You can also create a custom administrator account interactively:
```powershell
python run.py create-admin
```

### 7. Run the Application
```powershell
python run.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🧪 Running Automated Tests

CampusConnect includes 24 automated unit and integration tests using **pytest**. Tests run against an isolated **in-memory SQLite database** (`sqlite:///:memory:`) so your development or production database is never modified or erased.

Execute the test suite with:
```powershell
python -m pytest -v
```

### Test Coverage Summary:
- **Authentication (`tests/test_auth.py`)**:
  - Werkzeug password hashing verification and salt security
  - Student registration and duplicate email rejection
  - Student login, session establishment, and logout
  - Administrator login and automatic redirection to admin hub
  - Invalid credential rejection
  - Role-based authorization and 403 Forbidden enforcement
- **Events Management (`tests/test_events.py`)**:
  - Public homepage status 200 and branding validation
  - About page rendering
  - Event title search and category filtering
  - Event details page rendering
  - 404 response for invalid event IDs
  - Admin event creation, modification, and deletion
  - Student restriction from admin event creation
- **Registrations & Capacities (`tests/test_registrations.py`)**:
  - Successful student registration and seat deduction
  - Prevention of duplicate active registrations
  - Enforcement of maximum seat capacity limits
  - Rejection of registrations for past events
  - Student registration cancellation and immediate seat recovery
  - Admin participant roster inspection

---

## 👥 User Workflows

### 🎓 Student Workflow
1. Navigate to `http://127.0.0.1:5000/` and click **"Join as Student"** or **"Sign Up"**.
2. Enter your Name, College Email, and Password.
3. Sign in on the **Login** page.
4. Browse upcoming events on the **Events** page. Use the category pills (*Technology*, *Cultural*, *Sports*, *Workshop*, *Seminar*) or the search bar.
5. Click **"View Details"** on any event to inspect venue, schedule, and live available seats.
6. Click **"Confirm Registration"**. Your seat is immediately secured and capacity reflects in real time.
7. Access the **Student Hub** (`/student/dashboard`) or **My Registrations** (`/student/registrations`) to review booked events.
8. If your schedule changes, click **"Cancel Registration"**; a confirmation modal will verify the action, update your status to `CANCELLED`, and replenish the seat for peers.

### 🛡️ Administrator Workflow
1. Log in with admin credentials (e.g., `admin@campusconnect.edu` / `Admin@123`).
2. You will be automatically redirected to the **Administrator Console** (`/admin/dashboard`).
3. View high-level metrics: Total Events, Student Accounts, Active Registrations, and Average Capacity Occupancy percentage.
4. Click **"+ Schedule New Event"** to create a new activity with date, start time, venue, description, category, and capacity.
5. In the Event Master Roster, click **"Roster (X)"** on any event to view the full student participant list with email addresses and registration timestamps.
6. Click **"Edit"** to update event details or adjust capacity (guarded so capacity cannot be decreased below current active enrollments).
7. Click **"Delete"** with modal confirmation to permanently remove an event and cascade-remove its registrations.

---

## 🌐 Production Deployment Guide

CampusConnect is pre-configured and tested for zero-downtime deployment on major cloud hosting platforms:

### A. Deploying on Vercel via GitHub (Serverless)
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare production deployment"
   git push origin main
   ```
2. **Import repository into Vercel**:
   - Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
   - Select your GitHub repository.
   - Framework Preset: **Other** (Vercel automatically detects `vercel.json` and `@vercel/python`).
   - Root Directory: `./` (Leave as default).
3. **Configure Environment Variables in Vercel Project Settings**:
   - `SECRET_KEY`: A strong random string (e.g., `openssl rand -hex 32`).
   - `FLASK_ENV`: `production`
   - `ALLOW_SQLITE_FALLBACK`: Set to `True` for instant zero-database testing (uses `/tmp/campusconnect.db`) or provide `DATABASE_URL` for managed MySQL/PostgreSQL.
   - `DATABASE_URL` *(Recommended for production)*: Connection string to your cloud MySQL or PostgreSQL instance (e.g., TiDB, Aiven, Supabase, Neon, Railway).
4. **Deploy**: Click **"Deploy"**. The app will be live with full routing and static assets handled seamlessly via `api/index.py` and `vercel.json`.

### B. Deploying on Render or Railway (Container / WSGI)
1. Connect your GitHub repository to Render or Railway.
2. The platform automatically detects `Procfile` (`web: gunicorn wsgi:app`) and installs `requirements.txt`.
3. Set environment variables:
   - `SECRET_KEY`: Your production secret key.
   - `FLASK_ENV`: `production`
   - `DATABASE_URL`: Your managed MySQL or PostgreSQL database URI.
   - `PORT`: Handled automatically by the host (defaults to `5000` locally).

---

## 🎓 College Viva Examination & Technical Defense Guide

This section is prepared specifically to help 2nd-year B.Tech CSE students answer technical questions from external examiners during project viva presentations:

### Q1: What software architecture does CampusConnect follow?
> **Answer:** CampusConnect adheres to the **Model-View-Template (MVT)** architecture (Flask's implementation of MVC). 
> - **Models (`app/models.py`)**: SQLAlchemy classes representing database entities (`User`, `Event`, `Registration`) with table relationships, constraints, and business logic methods.
> - **Views / Controllers (`app/*/routes.py`)**: Flask Blueprints encapsulating route endpoints, authorization decorators, request validation, and database transactions.
> - **Templates (`app/templates/`)**: Jinja2 HTML templates displaying data dynamically using components and layouts extending `base.html`.

### Q2: Why was Flask chosen instead of Java Spring Boot or Django?
> **Answer:** Flask is a minimalist Python framework that provides explicit control over every architectural component. Unlike Spring Boot, which involves significant boilerplate, heavy XML/annotation layers, and high JVM RAM consumption, or Django, which has a rigid monolithic structure, Flask allows students to cleanly demonstrate core computer science concepts—Application Factory Pattern, Blueprints, custom decorators, connection pooling, and CSRF token lifecycles—with minimal overhead.

### Q3: How does the system prevent race conditions and overbooking when seats are limited?
> **Answer:** Overbooking prevention is enforced at both the application and database layer:
> 1. In `app/models.py`, `available_seats` is dynamically derived: `max(0, capacity - active_registrations_count)`.
> 2. The `can_register()` method verifies that `is_full` is False and the event is not in the past.
> 3. Active registrations are committed within atomic database transactions. If an error occurs, `db.session.rollback()` ensures database integrity.
> 4. In production with high concurrency, MySQL row-level locking (`SELECT ... FOR UPDATE`) is integrated to serialize seat allocations.

### Q4: How is security implemented for authentication and forms?
> **Answer:**
> - **Password Hashing:** Passwords are never stored as plain text. Werkzeug uses the PBKDF2/scrypt one-way key derivation function with unique cryptographic salts, making them immune to dictionary and rainbow-table attacks.
> - **CSRF Protection:** Every POST form includes an encrypted CSRF token generated by Flask-WTF and synchronized with user session state to prevent Cross-Site Request Forgery.
> - **Role-Based Access Control (RBAC):** Custom decorators (`@admin_required`, `@student_required`) check user roles before allowing access to administrative routes, issuing HTTP 403 Forbidden responses upon unauthorized attempts.
> - **Open Redirect Prevention:** The `is_safe_url()` utility inspects redirect query parameters (`next=...`) to verify the destination matches the host domain.

### Q5: What database normalization and indexing strategies were used?
> **Answer:**
> - The database schema is normalized up to **Third Normal Form (3NF)**:
>   - `users` stores identity and authentication credentials.
>   - `events` stores event scheduling and venue specifications.
>   - `registrations` acts as an associative entity (junction table) resolving the many-to-many relationship between students and events.
> - Indexes are explicitly defined on frequently queried columns: `users.email` (unique index), `events.title`, `events.category`, `events.event_date`, and a composite index `idx_user_event_status` on `(user_id, event_id, status)` for fast student registration lookups.

---

## 🔧 Troubleshooting & FAQ

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password in `.env` | Update `DB_PASSWORD` in `.env` with your local MySQL password. If left blank, CampusConnect automatically falls back to SQLite so your app keeps running. |
| `Can't create database 'campusconnect'` | Database already exists or MySQL service stopped | Verify MySQL80 is running via Windows Services (`Get-Service MySQL80`). If the database exists, the app connects directly to it. |
| Port 5000 is occupied | Another process or AirPlay/Windows service is using port 5000 | Set a different port in `.env` (e.g. `PORT=5001`) or run: `python run.py` with `$env:PORT=5001`. |
| PowerShell script execution error | Windows execution policy blocks `.venv\Scripts\Activate.ps1` | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in your PowerShell window. |

---

## 📄 License & Academic Attribution
Developed as an open-source academic project for B.Tech Computer Science and Engineering students. Free to use, adapt, and demonstrate for university submissions and technical interviews.
