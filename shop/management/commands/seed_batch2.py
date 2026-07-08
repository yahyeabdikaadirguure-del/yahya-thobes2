"""Load the Emirati/Cuman cijsi hose (Kids) and the shoe stock."""
from django.core.management.base import BaseCommand

from shop.models import Product

EMIRATI_HOSE = {
    "30": 15, "32": 14, "34": 7, "36": 14, "40": 4,
    "42": 2, "44": 2, "46": 1, "48": 2, "50": 1,
}

CUMAN_HOSE = {
    "30": 1, "32": 1, "34": 3, "36": 1, "38": 1,
    "40": 1, "42": 2, "44": 1, "48": 1, "50": 1,
}

SHOES = {
    "Shoe 40": 5, "Shoe 41": 5, "Shoe 42": 12, "Shoe 43": 19,
    "Shoe 44": 24, "Shoe 45": 21, "Shoe 46": 9,
}


class Command(BaseCommand):
    help = "Load Emirati/Cuman cijsi hose (Kids) and shoe stock"

    def add_arguments(self, parser):
        parser.add_argument("--emirati-price", type=int, default=1000)
        parser.add_argument("--cuman-price", type=int, default=1000)
        parser.add_argument("--shoe-price", type=int, default=1500)

    def _load(self, name, category, items, price, low_at=1):
        created = pieces = skipped = 0
        for size, qty in sorted(items.items()):
            _, was_created = Product.objects.get_or_create(
                name=name, size=size,
                defaults={"category": category, "price": price,
                          "stock": qty, "low_at": low_at},
            )
            if was_created:
                created += 1
                pieces += qty
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"{name}: added {created} lines ({pieces} pieces) at KSh {price}, "
            f"skipped {skipped} existing."))

    def handle(self, *args, **opts):
        self._load("Emirati Cijsi Hose", "Kids", EMIRATI_HOSE, opts["emirati_price"])
        self._load("Cuman Cijsi Hose", "Kids", CUMAN_HOSE, opts["cuman_price"])
        self._load("Shoes", "Shoes", SHOES, opts["shoe_price"], low_at=3)
        self.stdout.write(self.style.WARNING(
            "Reminder: Cuman Cijsi Hose size 46 was unclear and NOT loaded."))
