# LibraryOS — Library Management System

Production-oriented Django 6 library software with role-based workspaces for students, librarians, and administrators.

## Features

- Role-aware authentication, profiles, password reset/change, and persistent sessions
- Catalogue CRUD with authors, categories, publishers, image uploads, search, filters, sorting, and pagination
- Borrow requests, reservations, issue/reject/return workflows, renewals, notifications, and automatic overdue fines
- Responsive Bootstrap UI, dashboard KPIs, category chart, customized Django administration, and SQLite storage

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/. Superusers are Admins automatically. Create student accounts through `/accounts/register/`; create Librarians through the Django admin by setting their role.

For deployment, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS` in the environment, and run `python manage.py collectstatic`.
