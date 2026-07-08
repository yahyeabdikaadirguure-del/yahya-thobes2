"""Remove seeded stock groups. Preview first, delete only with --yes.

    python manage.py clean_stock --shaal                 # preview only
    python manage.py clean_stock --shaal --yes           # actually delete
    python manage.py clean_stock --shaal --hose --shoes --samples --yes
"""
from django.core.management.base import BaseCommand

from shop.models import Product

SAMPLE_NAMES = [
    "Emirati Kanzu, White", "Saudi Thobe, White collar", "Moroccan Thobe, Beige",
    "Omani Kanzu with tassel", "Black Thobe, gold embroidery", "Men's Jalabiya, Grey",
    "Bisht (men's cloak), Black-gold", "Kufi cap, White crochet",
    "Barghashia cap, Embroidered", "Shemagh scarf, Red-white", "Tasbih prayer beads",
    "Men's prayer mat, Padded", "Boys' Kanzu, White",
]


class Command(BaseCommand):
    help = "Remove seeded stock groups (preview unless --yes)"

    def add_arguments(self, parser):
        parser.add_argument("--shaal", action="store_true", help="all Shaal category items")
        parser.add_argument("--hose", action="store_true", help="Emirati/Cuman Cijsi Hose")
        parser.add_argument("--shoes", action="store_true", help="the seeded 'Shoes' lines")
        parser.add_argument("--samples", action="store_true", help="the original demo products")
        parser.add_argument("--yes", action="store_true", help="actually delete")

    def handle(self, *args, **o):
        targets = Product.objects.none()
        if o["shaal"]:
            targets = targets | Product.objects.filter(category="Shaal")
        if o["hose"]:
            targets = targets | Product.objects.filter(
                name__in=["Emirati Cijsi Hose", "Cuman Cijsi Hose"])
        if o["shoes"]:
            targets = targets | Product.objects.filter(name="Shoes", category="Shoes")
        if o["samples"]:
            targets = targets | Product.objects.filter(name__in=SAMPLE_NAMES)

        if not targets.exists():
            self.stdout.write("Nothing matched. Use flags: --shaal --hose --shoes --samples")
            return

        self.stdout.write(f"Matched {targets.count()} product lines:")
        for p in targets.order_by("name", "size"):
            self.stdout.write(f"  - {p} | {p.category} | stock {p.stock}")

        if o["yes"]:
            n, _ = targets.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted."))
        else:
            self.stdout.write(self.style.WARNING(
                "PREVIEW ONLY - nothing deleted. Re-run with --yes to delete."))
