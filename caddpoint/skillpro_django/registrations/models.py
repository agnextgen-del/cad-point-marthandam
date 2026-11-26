import datetime
import re

from django.db import models, transaction
from django.db.models import F

APP_ID_PREFIX = "Sk-2027-"          # Application IDs look like Sk-2027-01, Sk-2027-02 ...
COUNTER_NAME = "skillpro2027"

YEARS = ("I", "II", "III", "IV", "Other")
BRANCHES = ("Marthandam", "Nagercoil", "Neyyattinkara", "Trivandrum")


class ApplicationCounter(models.Model):
    """One row that holds the last Application ID number handed out (never goes back down)."""
    name = models.CharField(max_length=50, unique=True)
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "skillpro_application_counter"

    def __str__(self):
        return f"{self.name}: {self.last_number}"


def _highest_existing_number():
    best = 0
    pattern = re.compile(r"^" + re.escape(APP_ID_PREFIX) + r"(\d+)$")
    for value in SkillProRegistration.objects.exclude(application_id__isnull=True) \
            .values_list("application_id", flat=True):
        m = pattern.match(value or "")
        if m:
            best = max(best, int(m.group(1)))
    return best


def next_application_id():
    """Return the next Sk-2027-XX id. MUST be called inside transaction.atomic().

    The UPDATE takes a database row lock, so two students submitting at the same moment are
    serialised: the second one waits for the first to commit and then gets the next number.
    If the registration later fails to save, the whole transaction rolls back and the number is
    not used up.
    """
    ApplicationCounter.objects.get_or_create(
        name=COUNTER_NAME, defaults={"last_number": _highest_existing_number()})
    ApplicationCounter.objects.filter(name=COUNTER_NAME).update(last_number=F("last_number") + 1)
    n = ApplicationCounter.objects.values_list("last_number", flat=True).get(name=COUNTER_NAME)
    return f"{APP_ID_PREFIX}{n:02d}"


class SkillProRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True)
    application_id = models.CharField(max_length=20, unique=True, null=True, blank=True,
                                      editable=False, db_index=True)
    student_name = models.CharField(max_length=80)
    college_name = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, unique=True)   # one registration per mobile number
    email = models.EmailField(max_length=120, unique=True)        # one registration per email
    # Address is no longer collected. The column is kept (empty for new rows) so old records keep their data.
    address = models.CharField(max_length=300, blank=True, default="")
    year = models.CharField(max_length=10, blank=True, default="")
    year_other = models.CharField(max_length=20, blank=True, default="")
    exam_branch = models.CharField(max_length=20, blank=True, default="")
    exam_date = models.DateField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "skillpro_registrations"
        ordering = ["-registration_date"]
        verbose_name = "Registration"

    def __str__(self):
        return f"{self.application_id or 'SP-%s' % self.registration_id} {self.student_name}"

    @property
    def year_display(self):
        if self.year == "Other" and self.year_other:
            return f"Other ({self.year_other})"
        return self.year

    def save(self, *args, **kwargs):
        if self.application_id:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            self.application_id = next_application_id()
            try:
                super().save(*args, **kwargs)
            except Exception:
                self.application_id = None
                raise
