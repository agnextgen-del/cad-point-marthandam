# Skill Pro Event – website popup + registration dashboard (Django)

## What you get
| Part | Where |
|---|---|
| Website with the poster popup + registration form | `CADD WEBSITE/index-poster.html` |
| Backend that saves each submission | `skillpro_django/` |
| Dashboard page inside your website (search, filter, delete, auto-refresh, **Excel + CSV download**) | `CADD WEBSITE/students-details/skillpro-dashboard.html` -> open `http://127.0.0.1:8000/students-details/skillpro-dashboard.html` |
| Same dashboard served by Django (alternative) | `http://127.0.0.1:8000/skillpro/registrations/` |

Flow: visitor opens the site -> poster popup -> **REGISTER NOW** -> form -> **SUBMIT** -> saved in the database ->
success message -> row appears in the dashboard -> you download it as Excel/CSV.

## Run it on your computer (2 minutes)
1. Install Python 3.10 or newer from python.org (Windows: tick "Add Python to PATH").
2. **Windows:** double-click `START-WINDOWS.bat`.  **Mac/Linux:** run `./START-MAC-LINUX.sh`.
3. First run only: choose a dashboard username and password when asked.
4. Open **http://127.0.0.1:8000/** (the website) – always use this address, not the file directly.
5. Submit a test registration, then open **http://127.0.0.1:8000/students-details/skillpro-dashboard.html** and log in with the username/password from step 3.

Dashboard buttons: **Download Excel (.xlsx)**, **CSV**, **Refresh**, search box, department filter, delete (✕).
Downloads contain exactly the rows matching your current search/filter (clear it to get everyone).

By default data is stored in a local SQLite file (`skillpro_django/db.sqlite3`) so it works instantly.

## Use MySQL instead
1. Create the database (MySQL Workbench / phpMyAdmin):
   ```sql
   CREATE DATABASE skillpro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'skillpro_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
   GRANT ALL PRIVILEGES ON skillpro_db.* TO 'skillpro_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. Edit `skillpro_django/.env`: delete the `DB_ENGINE=sqlite` line and un-comment/fill the `DB_*` lines.
3. Run the start script again (it creates the table `skillpro_registrations` automatically).

## Put it on your live website
1. Host the Django app on a server that can run Python (VPS, PythonAnywhere, Render, etc.) with MySQL.
2. `.env` on the server – copy `.env.example`, set `DJANGO_DEBUG=False`, a long `DJANGO_SECRET_KEY`, your domain in
   `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and the MySQL `DB_*` values.
3. `python manage.py migrate`, `python manage.py ensure_admin`, `python manage.py collectstatic`.
4. Run: `gunicorn config.wsgi:application -b 127.0.0.1:8000` (Linux) or `waitress-serve --listen=127.0.0.1:8000 config.wsgi:application` (Windows).
5. Put Nginx/Apache with HTTPS in front. Serve your website files normally, and proxy `/api/`, `/skillpro/`, `/accounts/`, `/admin/`
   to Django. Because the popup posts to `/api/skillpro/register` (same domain) no other change is needed.
   If the API is on a different domain, set `data-api-url="https://api.yourdomain.com/api/skillpro/register"` in `index-poster.html`.
6. To show the popup on your home page, use the contents of `index-poster.html` as `index.html` (it is your index plus the popup).

## Safety notes
* The dashboard needs a staff login and holds personal data – never link it from the public site.
* One registration per phone number and per email (database-enforced). Duplicates show an error under the field.
* The success message appears only after the database confirms the row was saved.
* Excel/CSV exports neutralise formula injection (cells starting with = + - @).
* `skillpro_django/.env` contains your secret key – don't share or upload it publicly.

## API contract (used by the popup)
`POST /api/skillpro/register` -> 201 saved | 400 invalid | 409 duplicate phone/email | 429 too many attempts | 500 server error.

## Dashboard page inside the website
`CADD WEBSITE/students-details/skillpro-dashboard.html` is a normal page in your site. It logs in with your Django staff account,
loads the registrations from the backend, refreshes itself every 30 seconds and offers Excel/CSV downloads.
It works when the website and Django share one address (Django serving the site locally, or Nginx/Apache sending
`/api/` and `/skillpro/` to Django on your live server). Opening the file directly or from Live Server will show a "could not reach server" message.
