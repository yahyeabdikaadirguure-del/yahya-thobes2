"""Wipe stock (and optionally sales). Preview unless --yes.

    python manage.py wipe_all                    # preview products
    python manage.py wipe_all --yes              # delete ALL products
    python manage.py wipe_all --sales --yes      # delete ALL products AND sales
User accounts are never touched.
"""
from django.core.management.base import BaseCommand

from shop.models import Product, Sale


class Command(BaseCommand):
    help = "Delete all products (and optionally all sales). Preview unless --yes."

    def add_arguments(self, parser):
        parser.add_argument("--sales", action="store_true",
                            help="also delete all sales history")
        parser.add_argument("--yes", action="store_true", help="actually delete")

    def handle(self, *args, **o):
        p_count = Product.objects.count()
        s_count = Sale.objects.count()
        self.stdout.write(f"Products in database: {p_count}")
        self.stdout.write(f"Sales records: {s_count} "
                          f"({'WILL be deleted' if o['sales'] else 'will be KEPT'})")

        if not o["yes"]:
            self.stdout.write(self.style.WARNING(
                "PREVIEW ONLY - nothing deleted. Re-run with --yes to wipe."))
            return

        Product.objects.all().delete()
        msg = f"Deleted {p_count} products."
        if o["sales"]:
            Sale.objects.all().delete()
            msg += f" Deleted {s_count} sales."
        self.stdout.write(self.style.SUCCESS(msg + " Staff accounts untouched."))
