"""Skill Pro registration API.

POST /api/skillpro/register -> 201 saved | 400 invalid | 409 duplicate | 429 too many | 500 error
GET  /api/skillpro/health   -> database check
"""
import datetime
import json
import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import BRANCHES, YEARS, SkillProRegistration

log = logging.getLogger("skillpro")

NAME_BAD = re.compile(r"[\d<>{}\[\]\\/@#$%^&*=+|~`_;:\"!?()]")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean(value):
    return CONTROL.sub("", str(value or "")).strip()


def normalize_phone(v):
    d = re.sub(r"[\s\-().]", "", str(v or ""))
    if re.fullmatch(r"\+91\d{10}", d):
        return d[3:]
    if re.fullmatch(r"91\d{10}", d):
        return d[2:]
    if re.fullmatch(r"0\d{10}", d):
        return d[1:]
    return d


def validate(data):
    errors = {}
    name = clean(data.get("student_name"))
    college = clean(data.get("college_name"))
    dept = clean(data.get("department"))
    phone = normalize_phone(data.get("phone_number"))
    email = clean(data.get("email")).lower()
    year = clean(data.get("year"))
    year_other = clean(data.get("year_other"))
    branch = clean(data.get("exam_branch"))
    exam_date_raw = clean(data.get("exam_date"))

    if not (2 <= len(name) <= 80) or NAME_BAD.search(name) or not any(c.isalpha() for c in name):
        errors["student_name"] = "Enter a valid full name (letters, spaces, . ' and - only)."
    if not (3 <= len(college) <= 150):
        errors["college_name"] = "Enter your college name (3-150 characters)."
    if not (2 <= len(dept) <= 100):
        errors["department"] = "Select or enter your department."
    if not PHONE_RE.match(phone):
        errors["phone_number"] = "Enter a valid 10-digit Indian mobile number."
    if len(email) > 120 or not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."

    if year not in YEARS:
        errors["year"] = "Please select your year."
    if year == "Other":
        if not (1 <= len(year_other) <= 20):
            errors["year_other"] = "Please enter your year (up to 20 characters)."
    else:
        year_other = ""
    if branch not in BRANCHES:
        errors["exam_branch"] = "Please select a branch."

    exam_date = None
    try:
        if len(exam_date_raw) != 10:
            raise ValueError
        exam_date = datetime.date.fromisoformat(exam_date_raw)
        if exam_date < timezone.localdate():
            errors["exam_date"] = "Exam date cannot be in the past."
    except ValueError:
        errors["exam_date"] = "Please select a valid exam date."

    return errors, dict(student_name=name, college_name=college, department=dept,
                        phone_number=phone, email=email, year=year, year_other=year_other,
                        exam_branch=branch, exam_date=exam_date)


def client_ip(request):
    if settings.SKILLPRO_TRUST_PROXY:
        fwd = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limited(ip, limit=8, window=60):
    key = f"skillpro-rl-{ip}"
    cache.add(key, 0, window)
    try:
        return cache.incr(key) > limit
    except ValueError:
        return False


@csrf_exempt            # public JSON API called from the static site; protected by validation + rate limit
@require_POST
def register(request):
    if rate_limited(client_ip(request)):
        return JsonResponse({"success": False, "message": "Too many attempts. Please try again in a minute."}, status=429)

    try:
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    if data.get("website"):  # honeypot field – real users never fill it
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    errors, row = validate(data)
    if errors:
        return JsonResponse({"success": False, "message": "Please correct the highlighted fields.",
                             "errors": errors}, status=400)

    try:
        with transaction.atomic():
            reg = SkillProRegistration.objects.create(**row)
    except IntegrityError:
        # Unique constraint hit: report which field is already registered.
        if SkillProRegistration.objects.filter(phone_number=row["phone_number"]).exists():
            return JsonResponse({"success": False, "field": "phone_number",
                                 "message": "This mobile number is already registered."}, status=409)
        if SkillProRegistration.objects.filter(email=row["email"]).exists():
            return JsonResponse({"success": False, "field": "email",
                                 "message": "This email address is already registered."}, status=409)
        log.exception("Integrity error")
        return JsonResponse({"success": False, "message": "Could not save your registration."}, status=500)
    except DatabaseError:
        log.exception("Database error")
        return JsonResponse({"success": False, "message": "Server error. Please try again later."}, status=500)

    log.info("Registration stored id=%s application_id=%s", reg.registration_id, reg.application_id)
    return JsonResponse({"success": True, "registration_id": reg.registration_id,
                         "application_id": reg.application_id,
                         "message": "Your Skill Pro Event registration has been submitted successfully."}, status=201)


@require_GET
def health(request):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "connected"})
    except DatabaseError:
        log.exception("Health check failed")
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)
