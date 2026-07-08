"""Bulk-load the shaal inventory:

    python manage.py seed_shaal              # price defaults to KSh 1500
    python manage.py seed_shaal --price 1800

Re-running is safe: existing shaal items (same name and size) are skipped.
"""
from collections import defaultdict

from django.core.management.base import BaseCommand

from shop.models import Product

# (size, color/style, quantity)
SHAAL_RAW = [
    (46, "Black", 1), (46, "White", 1), (46, "Grey", 1),
    (48, "Black", 2), (48, "White", 1), (48, "Grey", 1),
    (50, "Tush Tush White", 1), (50, "Black", 2), (50, "White", 1),
    (52, "Black", 2), (52, "White", 1), (52, "Tush Tush Green", 1),
    (54, "Grey", 2), (54, "Blue", 2), (54, "Blue Sky", 1),
    (56, "Blue Sky", 1), (56, "Green", 1),
    (58, "Black", 1), (60, "Brown", 2), (60, "Black", 1),
    (34, "Grey", 1), (34, "White", 2), (34, "Black", 2), (34, "Brown", 1),
    (34, "Blue Sky", 2), (34, "White", 1), (34, "Brown", 1),
    (36, "Green", 4), (36, "White", 4), (36, "Grey", 3),
    (36, "Emirati Grey", 1), (36, "Brown", 1), (36, "Emirati White", 1),
    (38, "Emirati White", 1), (38, "Blue Emirati", 2), (38, "Faraj White", 1),
    (38, "Blue Sky", 3), (38, "Tush Tush Green", 1), (38, "Tush Tush Blue", 1),
    (38, "Faraj Grey Dark", 1), (38, "White", 1), (38, "Fananx White", 1),
    (40, "Tush Tush White", 2), (40, "Black", 1), (40, "White", 1), (40, "Grey", 1),
    (42, "Tush Tush Green", 1), (42, "White", 3), (42, "Black", 1),
    (44, "Blue Sky", 1), (44, "Black", 1), (44, "White", 1), (44, "Fanan White", 1),
    (20, "Blue", 1), (20, "Black", 1),
    (22, "Blue", 2), (22, "Grey", 3),
    (24, "White", 1), (26, "Grey", 2), (28, "Grey", 1), (28, "Blue", 1),
    (20, "Green", 1), (20, "White", 1), (20, "Grey", 1),
    (22, "Brown", 1), (22, "Blue", 1), (22, "Green Light", 1),
    (30, "Blue", 2), (30, "Green", 2), (30, "White", 1),
    (30, "Tush Tush White", 1), (30, "Grey Dark", 1), (30, "Faraj White", 1),
    (32, "Grey Dark", 1), (32, "Black", 2), (32, "Tush Tush Blue", 1),
    (32, "Emirati Grey", 1), (32, "Emirati Blue", 1), (32, "White", 3),
    (32, "Blue Sky", 1), (32, "White Emirati", 1), (32, "Brown", 1),
    (32, "Blue Sky", 1),
]


class Command(BaseCommand):
    help = "Bulk-load the shaal inventory"

    def add_arguments(self, parser):
        parser.add_argument("--price", type=int, default=1500,
                            help="price in KSh for every shaal (default 1500)")

    def handle(self, *args, **opts):
        price = opts["price"]
        # merge duplicate size+color entries (e.g. 34 White appears twice)
        merged = defaultdict(int)
        for size, color, qty in SHAAL_RAW:
            merged[(str(size), color)] += qty

        created = skipped = total_pieces = 0
        for (size, color), qty in sorted(merged.items()):
            _, was_created = Product.objects.get_or_create(
                name=f"Shaal {color}", size=size,
                defaults={"category": "Shaal", "price": price,
                          "stock": qty, "low_at": 1},
            )
            if was_created:
                created += 1
                total_pieces += qty
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Added {created} shaal lines ({total_pieces} pieces) at KSh {price}. "
            f"Skipped {skipped} that already existed."))
