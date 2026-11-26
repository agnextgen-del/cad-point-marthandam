"""JSON endpoints used by the dashboard page in the website (students-details/skillpro-dashboard.html)."""
import json
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .dashboard import _filtered
from .models import SkillProRegistration
from .views import client_ip


def _is_staff(u):
    return u.is_authenticated and u.is_active and u.is_staff


def staff_json(view):
    @wraps(view)
    def wrapper(request, *a, **k):
        if not _is_staff(request.user):
            return JsonResponse({"success": False, "message": "Please log in."}, status=401)
        return view(request, *a, **k)
    return wrapper


@ensure_csrf_cookie
@require_GET
def session(request):
    u = request.user
    return JsonResponse({"authenticated": _is_staff(u), "username": u.username if _is_staff(u) else "",
                         "csrf": get_token(request)})


@require_POST
def login_api(request):
    key = f"skillpro-login-{client_ip(request)}"
    cache.add(key, 0, 300)
    if cache.incr(key) > 10:
        return JsonResponse({"success": False, "message": "Too many attempts. Wait 5 minutes."}, status=429)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
    user = authenticate(request, username=str(data.get("username", "")), password=str(data.get("password", "")))
    if user is None or not user.is_staff:
        return JsonResponse({"success": False, "message": "Wrong username or password."}, status=401)
    login(request, user)
    return JsonResponse({"success": True, "username": user.username, "csrf": get_token(request)})


@require_POST
def logout_api(request):
    logout(request)
    return JsonResponse({"success": True})


@staff_json
@require_GET
def list_api(request):
    qs, q, dept = _filtered(request)
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    rows = [{
        "id": r.registration_id, "code": r.application_id or f"SP-{r.registration_id}",
        "application_id": r.application_id or "", "student_name": r.student_name,
        "college_name": r.college_name, "department": r.department, "phone_number": r.phone_number,
        "email": r.email, "address": r.address,
        "year": r.year, "year_other": r.year_other, "year_display": r.year_display,
        "exam_branch": r.exam_branch,
        "exam_date": r.exam_date.strftime("%d %b %Y") if r.exam_date else "",
        "registered_on": localtime(r.registration_date).strftime("%d %b %Y, %I:%M %p"),
    } for r in page]
    return JsonResponse({
        "rows": rows, "page": page.number, "pages": page.paginator.num_pages,
        "total": SkillProRegistration.objects.count(),
        "today": SkillProRegistration.objects.filter(registration_date__date=timezone.localdate()).count(),
        "shown": page.paginator.count,
        "departments": sorted(SkillProRegistration.objects.order_by().values_list("department", flat=True).distinct()),
        "refreshed": localtime().strftime("%d %b %Y, %I:%M:%S %p"),
    })


@staff_json
@require_POST
def delete_api(request, pk):
    deleted, _ = SkillProRegistration.objects.filter(pk=pk).delete()
    return JsonResponse({"success": bool(deleted)}, status=200 if deleted else 404)
