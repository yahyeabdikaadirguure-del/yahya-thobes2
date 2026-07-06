"""Create the staff roles and (optionally) staff accounts.

    python manage.py setup_roles
    python manage.py setup_roles --cashier ali --password 1234
    python manage.py setup_roles --shopkeeper fatima --password 1234

Roles:
  Admin       = Django superuser (createsuperuser). Full access, can delete.
  Shopkeeper  = sees Dashboard, Insights, Inventory (add/edit), can undo sales.
                Cannot delete products (admin only).
  Cashier     = sees Dashboard and Record sale only.
"""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set up Cashier and Shopkeeper roles, optionally create a staff user"

    def add_arguments(self, parser):
        parser.add_argument("--cashier", type=str, help="username for a new cashier")
        parser.add_argument("--shopkeeper", type=str, help="username for a new shopkeeper")
        parser.add_argument("--password", type=str, help="password for the new user")

    def handle(self, *args, **opts):
        cashier_group, _ = Group.objects.get_or_create(name="Cashier")
        shopkeeper_group, _ = Group.objects.get_or_create(name="Shopkeeper")
        self.stdout.write(self.style.SUCCESS("Roles ready: Cashier, Shopkeeper."))

        for role, group in (("cashier", cashier_group), ("shopkeeper", shopkeeper_group)):
            username = opts.get(role)
            if not username:
                continue
            password = opts.get("password")
            if not password:
                self.stdout.write(self.style.ERROR(
                    f"Provide --password to create the {role} '{username}'."))
                continue
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_staff = False
            user.save()
            user.groups.clear()
            user.groups.add(group)
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(
                f"{verb} {role} '{username}'. They can now sign in."))
