# Arthy Hotel

A Django web application for hotel room browsing, booking, and staff reservation management.

## Features

- Customer registration and authentication
- Room catalog with search, availability filters, and date conflict checks
- Booking flow with receipt upload and PDF confirmation slip
- Customer booking history with pending cancellation
- Staff dashboard for approving or rejecting reservations
- Staff room inventory management (create, edit, delete)

## Tech stack

- Python / Django 6
- SQLite (local development) or PostgreSQL (production)
- Pillow for image uploads
- ReportLab for PDF slips
- WhiteNoise for static files in production

## Project structure

```
hotel_system/          # Django project settings
hotel/
  models/              # Room, Profile, Booking
  views/               # Auth, customer, booking, room, staff views
  forms/               # Form definitions
  services/            # Availability logic and PDF generation
  templates/
    base.html
    partials/
    pages/
  tests/
static/
  css/                 # Stylesheets
  photos/              # Logo, hero, and default room images
  js/
```

## Local setup

1. Create and activate a virtual environment.

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser for staff access:

   ```bash
   python manage.py createsuperuser
   ```

   Staff users must have `is_staff=True` in Django admin.

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Visit `http://127.0.0.1:8000/`

## Running tests

```bash
python manage.py test hotel
```

## Production deployment

The project includes Render-friendly settings:

- Set `DATABASE_URL` for PostgreSQL
- Set `SECRET_KEY`, `DEBUG=False`, and `ALLOWED_HOSTS`
- Run `build.sh` to install dependencies, collect static files, and migrate

## Security notes

- Never commit real credentials. Use `.env` locally and platform secrets in production.
- Public registration always creates customer accounts. Staff access is granted only via `is_staff`.
- Booking slips are restricted to the booking owner or staff users.
