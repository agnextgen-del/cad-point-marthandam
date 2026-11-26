import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import localtime

from .models import SkillProRegistration

admin.site.site_header = "Skill Pro Event – Admin"
admin.site.site_title = "Skill Pro Admin"


@admin.register(SkillProRegistration)
class SkillProRegistrationAdmin(admin.ModelAdmin):
    list_display = ("application_id", "student_name", "college_name", "department",
                    "phone_number", "email", "year_display", "exam_branch", "exam_date",
                    "registration_date")
    list_display_links = ("application_id", "student_name")
    search_fields = ("application_id", "student_name", "college_name", "phone_number", "email")
    list_filter = ("year", "exam_branch", "exam_date", "department", "registration_date")
    readonly_fields = ("application_id", "registration_date")
    fields = ("application_id", "student_name", "college_name", "department", "phone_number", "email",
              "year", "year_other", "exam_branch", "exam_date", "address", "registration_date")
    ordering = ("-registration_id",)
    actions = ["export_csv"]

    @admin.display(description="Year", ordering="year")
    def year_display(self, obj):
        return obj.year_display

    @admin.action(description="Download selected registrations as CSV")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="skillpro_registrations.csv"'
        resp.write("\ufeff")  # BOM so Excel opens UTF-8 correctly
        w = csv.writer(resp)
        w.writerow(["Application ID", "Name", "College", "Department", "Phone", "Email", "Year",
                    "Other Year", "Exam Branch", "Exam Date", "Registered on"])
        for r in queryset.order_by("registration_id"):
            w.writerow([r.application_id or "", r.student_name, r.college_name, r.department,
                        r.phone_number, r.email, r.year, r.year_other, r.exam_branch,
                        r.exam_date.strftime("%d-%m-%Y") if r.exam_date else "",
                        localtime(r.registration_date).strftime("%Y-%m-%d %H:%M")])
        return resp
