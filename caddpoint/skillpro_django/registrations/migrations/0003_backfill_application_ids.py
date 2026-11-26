import re

from django.db import migrations

PREFIX = "Sk-2027-"
COUNTER = "skillpro2027"


def backfill(apps, schema_editor):
    """Give every existing registration an Application ID (oldest first) and start the counter after them."""
    Reg = apps.get_model("registrations", "SkillProRegistration")
    Counter = apps.get_model("registrations", "ApplicationCounter")

    pattern = re.compile(r"^" + re.escape(PREFIX) + r"(\d+)$")
    highest = 0
    for value in Reg.objects.exclude(application_id__isnull=True).values_list("application_id", flat=True):
        m = pattern.match(value or "")
        if m:
            highest = max(highest, int(m.group(1)))

    n = highest
    for reg in Reg.objects.filter(application_id__isnull=True).order_by("registration_id"):
        n += 1
        reg.application_id = f"{PREFIX}{n:02d}"
        reg.save(update_fields=["application_id"])

    counter, created = Counter.objects.get_or_create(name=COUNTER, defaults={"last_number": n})
    if not created and counter.last_number < n:
        counter.last_number = n
        counter.save(update_fields=["last_number"])


class Migration(migrations.Migration):
    dependencies = [("registrations", "0002_skillpro_exam_fields")]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
