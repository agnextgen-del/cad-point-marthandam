"""Creates the dashboard login the first time (skipped if an admin already exists)."""
from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the dashboard admin login if none exists yet."

    def handle(self, *args, **opts):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Dashboard admin login already exists.")
            return
        print("\n=== Create your dashboard login ===")
        username = input("Choose a username [admin]: ").strip() or "admin"
        while True:
            pw = getpass("Choose a password (min 8 characters): ")
            if len(pw) < 8:
                print("Too short, try again.")
            elif pw != getpass("Type the password again: "):
                print("Passwords did not match, try again.")
            else:
                break
        User.objects.create_superuser(username=username, email="", password=pw)
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' created."))
