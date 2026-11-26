"""Staff-only dashboard: list, search, filter, delete, and download (Excel / CSV)."""
import csv
import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .models import BRANCHES, YEARS, SkillProRegistration

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="/accounts/login/")

HEADERS = ["S.No", "Application ID", "Student Name", "College Name", "Department",
           "Phone Number", "Email ID", "Year", "Other Year", "Exam Branch", "Exam Date", "Registered On"]


def _filtered(request):
    qs = SkillProRegistration.objects.all()
    q = request.GET.get("q", "").strip()
    dept = request.GET.get("dept", "").strip()
    year = request.GET.get("year", "").strip()
    branch = request.GET.get("branch", "").strip()
    exam_date = request.GET.get("exam_date", "").strip()
    if q:
        qs = qs.filter(Q(application_id__icontains=q) | Q(student_name__icontains=q) |
                       Q(college_name__icontains=q) | Q(phone_number__icontains=q) |
                       Q(email__icontains=q))
    if dept:
        qs = qs.filter(department=dept)
    if year in YEARS:
        qs = qs.filter(year=year)
    if branch in BRANCHES:
        qs = qs.filter(exam_branch=branch)
    if exam_date:
        try:
            qs = qs.filter(exam_date=datetime.date.fromisoformat(exam_date))
        except ValueError:
            qs = qs.none()
    return qs, q, dept


def _rows(qs):
    """Yield one export row per registration (oldest first, numbered from 1)."""
    for i, r in enumerate(qs.order_by("registration_id"), start=1):
        yield [i, r.application_id or f"SP-{r.registration_id}", r.student_name, r.college_name,
               r.department, r.phone_number, r.email, r.year, r.year_other, r.exam_branch,
               r.exam_date.strftime("%d-%m-%Y") if r.exam_date else "",
               localtime(r.registration_date)]


def _csv_safe(v):
    """Stop spreadsheet formula injection: text starting with = + - @ is prefixed with '."""
    return "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r") else v


@staff_required
def dashboard(request):
    qs, q, dept = _filtered(request)
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    today = timezone.localdate()
    return render(request, "registrations/dashboard.html", {
        "page": page, "q": q, "dept": dept, "querystring": params.urlencode(),
        "year": request.GET.get("year", "").strip(), "branch": request.GET.get("branch", "").strip(),
        "exam_date": request.GET.get("exam_date", "").strip(),
        "years": YEARS, "branches": BRANCHES,
        "total": SkillProRegistration.objects.count(),
        "today": SkillProRegistration.objects.filter(registration_date__date=today).count(),
        "shown": qs.count(),
        "departments": SkillProRegistration.objects.order_by().values_list("department", flat=True).distinct(),
        "now": timezone.localtime(),
    })


@staff_required
def export_csv(request):
    qs, _, _ = _filtered(request)
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="skillpro_registrations.csv"'
    resp.write("\ufeff")  # BOM so Excel reads UTF-8 correctly
    w = csv.writer(resp)
    w.writerow(HEADERS)
    for row in _rows(qs):
        row[-1] = row[-1].strftime("%d-%m-%Y %I:%M %p")
        w.writerow([_csv_safe(v) for v in row])
    return resp


@staff_required
def export_excel(request):
    """Real .xlsx workbook: styled header, frozen top row, filters, sensible widths."""
    qs, _, _ = _filtered(request)
    wb = Workbook()
    ws = wb.active
    ws.title = "Skill Pro Registrations"
    ws.append(HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="0A1A4F")
        c.alignment = Alignment(horizontal="center", vertical="center")

    widths = [len(h) for h in HEADERS]
    for row in _rows(qs):
        row[-1] = row[-1].replace(tzinfo=None)          # Excel has no time zones
        ws.append(row)
        r = ws.max_row
        for col, v in enumerate(row, start=1):
            cell = ws.cell(row=r, column=col)
            if isinstance(v, str):
                cell.data_type = "s"                     # always plain text, never a formula
                widths[col - 1] = max(widths[col - 1], min(len(v), 60))
        ws.cell(row=r, column=len(HEADERS)).number_format = "dd-mmm-yyyy hh:mm AM/PM"

    widths[-1] = 22
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w + 3
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    buf = BytesIO()
    wb.save(buf)
    resp = HttpResponse(buf.getvalue(),
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="skillpro_registrations.xlsx"'
    return resp


@staff_required
@require_POST
def delete_registration(request, pk):
    reg = get_object_or_404(SkillProRegistration, pk=pk)
    label = f"{reg.application_id or 'SP-%s' % reg.registration_id} ({reg.student_name})"
    reg.delete()
    messages.success(request, f"Deleted registration {label}.")
    nxt = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        nxt = reverse("skillpro-dashboard")
    return redirect(nxt)
