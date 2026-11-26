"""Django settings for the Skill Pro registration API."""
import os
from pathlib import Path

import django
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
if not DEBUG and SECRET_KEY == "dev-only-change-me":
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY in .env before running with DJANGO_DEBUG=False.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "registrations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",          # must be above CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

# ---- Database: MySQL by default; set DB_ENGINE=sqlite for a quick local test ----
if os.getenv("DB_ENGINE", "mysql") == "sqlite":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
    if django.VERSION >= (5, 1):
        # Simultaneous submissions queue up for the write lock instead of failing with "database is locked".
        DATABASES["default"]["OPTIONS"] = {"transaction_mode": "IMMEDIATE", "timeout": 20}
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "skillpro_db"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }}

# ---- CORS: which websites may call the API ----
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)
CORS_URLS_REGEX = r"^/api/.*$"

# ---- Misc ----
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024

# Set to True only when Django sits behind Nginx/Apache that sets X-Forwarded-For.
SKILLPRO_TRUST_PROXY = os.getenv("SKILLPRO_TRUST_PROXY", "False") == "True"

if not DEBUG:
    SESSION_COOKIE_SECURE = os.getenv("DJANGO_HTTPS", "True") == "True"
    CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
    CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

# ---- Login for the registrations page ----
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/skillpro/registrations/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ---- Serve the website files from Django (local testing) ----
SITE_DIR = BASE_DIR.parent / "CADD WEBSITE"
HOME_PAGE = os.getenv("SKILLPRO_HOME_PAGE", "index-poster.html")
SERVE_SITE = os.getenv("SERVE_SITE", str(DEBUG)) == "True"
