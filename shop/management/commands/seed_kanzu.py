"""Load the full kanzu/thobe inventory. Safe to re-run (existing items skipped)."""
from collections import defaultdict

from django.core.management.base import BaseCommand

from shop.models import Product

# (name, size, price, qty) — exact names as recorded in the shop
DATA = [
("Abadi [Black]","54-20",3000,6),("Abadi [Black]","54-22",3000,8),
("Abadi [Black]","56-20",3000,1),("Abadi [Black]","56-20",3000,2),
("Abadi [Black]","56-22",3000,6),("Abadi [Black]","58-20",3000,8),
("Abadi [Black]","58-22",3000,7),("Abadi [Black]","60-24",3000,1),
("Abadi [MInt]","54-22",3000,2),("Abadi [MInt]","58-20",3000,1),
("Abadi [MInt]","60-22",3000,2),("Abadi [MInt]","62-24",3000,1),
("Abadi [White]","62-24",3000,1),("Abadi [white]","54-22",3000,2),
("Abadi [white]","54-24",3000,4),("Abadi [white]","56-20",3000,2),
("Abadi [white]","58-20",3000,1),("Abadi [white]","58-22",3000,5),
("Abadi [white]","60-20",3000,1),("Abadi [white]","60-22",3000,7),
("Abadi [white]","62-28",3000,1),("Abadi brown","54-22",2500,1),
("Abadi brown","58-20",2500,2),("Abadi brown","62-22",2500,1),
("Abadi cream","56-20",2500,2),("Abadi cream","58-20",2500,1),
("Abadi cream","58-22",2500,2),("Abadi cream","60-20",2500,1),
("Abadi cream","60-22",2500,3),("Abadi navy","54-20",2500,1),
("Abadi navy","56-20",2500,1),("Abadi navy","58-20",2500,2),
("Abadi navy","58-22",2500,1),("Abadi navy","60-22",2500,2),
("Abadi navy","62-22",2500,2),("Emirati [black]","54-24",3000,1),
("Emirati [black]","58-22",3000,2),("Emirati [black]","62-22",3000,1),
("Emirati[black]","54-22",3000,1),("Emirati[black]","56-20",3000,4),
("Emirati[black]","56-22",3000,2),("Emirati[black]","58-20",3000,1),
("Kuwaiti [Black]","54-22",2500,1),("Kuwaiti [Black]","60-22",2500,1),
("Kuwaiti [Blue]","58-22",2500,1),("Kuwaiti [Blue]","60-22",2500,4),
("Kuwaiti [Brown]","60-22",2500,1),("Kuwaiti [Brown]","62-22",2500,1),
("Kuwaiti [Dark-Brown]","58-22",2500,4),("Kuwaiti [Gray]","60-22",2500,5),
("Kuwaiti [Green]","60-22",2500,2),("Kuwaiti [White]","54-22",2500,4),
("Kuwaiti [White]","57-22",2500,1),("Kuwaiti [White]","58-20",2500,6),
("Kuwaiti [White]","60-20",2500,5),("Kuwaiti [White]","60-22",2500,5),
("Kuwaiti [White]","62-22",2500,2),("Kuwaiti [cream]","54-22",2500,4),
("Kuwaiti [cream]","56-22",2500,2),("Kuwaiti [cream]","56-22",2500,2),
("Kuwaiti [cream]","58-22",2500,5),("Kuwaiti [cream]","60-20",2500,2),
("Kuwaiti [cream]","60-22",2500,4),("Kuwaiti [cream]","62-22",2500,1),
("Kuwaiti [gray]","54-22",2500,1),("Kuwaiti [gray]","58-22",2500,3),
("Kuwaiti [green light]","54-24",2500,1),("Kuwaiti [green light]","60-22",2500,4),
("Kuwaiti [green light]","62-22",2500,1),("Kuwaiti [white]","56-20",3000,1),
("Qatari Black","56-20",2500,1),("Qatari Black","56-22",2500,1),
("Qatari Black","58-20",2500,1),("Qatari Black","58-22",2500,2),
("Qatari Black","58-24",2500,1),("Qatari Black","60-22",2500,1),
("Qatari black","60-20",2500,5),("Qatari cream","54-22",2500,1),
("Qatari cream","54-24",3000,3),("Qatari cream","56-20",2500,1),
("Qatari cream","56-20",2500,1),("Qatari cream","60-22",2500,2),
("Qatari cream","62-22",2500,2),("Qatari cream tush","56-20",2500,1),
("Qatari cream tush","60-20",2500,1),("Qatari cream tush","60-22",2500,2),
("Qatari white","54-24",3000,3),("Saudi","54-20",2500,2),
("Saudi","54-22",2500,7),("Saudi","54-24",2500,2),
("Saudi","56-20",2500,5),("Saudi","56-22",2500,12),
("Saudi","58-20",2500,3),("Saudi","60-20",2500,3),
("Saudi","60-22",2500,8),("Saudi","60-24",2500,2),
("Saudi","60-26",2500,1),("Saudi qoor taag cream tush","54-22",2500,7),
("abadi white","60-24",3000,1),("cimaamado koofiyad","-",1200,12),
("emirati[black]","60-22",3000,2),("qatari cream","54-20",3000,1),
("qatari white","58-22",3000,1),("saudi qoor taag","58-22",2500,1),
("saudi qoor taag black","58-20",2500,1),
("saudi qoor taag black tush","56-20",2500,1),
("saudi qoor taag black tush","60-20",2500,1),
("saudi qoor taag cream","58-20",2500,2),
("saudi qoor taag cream","60-20",2500,1),
("saudi qoor taag cream tush","54-22",2500,2),
("saudi qoor taag cream tush","56-20",2500,5),
("saudi qoor taag cream tush","56-22",2500,2),
("saudi qoor taag cream tush","58-20",2500,3),
("saudi qoor taag cream tush","60-20",2500,5),
("saudi qoor taag green","56-20",2500,1),
("saudi qoor taag green tush","58-20",2500,1),
("saudi qoor taag grey dark","58-20",2500,1),
("saudi qoor taag grey dark","60-22",2500,1),
("saudi qoor taag grey tush","60-20",2500,1),
("saudi qoor taag huruud","54-22",2500,1),
("saudi qoor taag huruud tush","54-20",2500,1),
("saudi qoor taag navy tush","60-22",2500,1),
("saudi qoor taag white","54-22",2500,3),
("saudi qoor taag white","56-20",2500,1),
("saudi qoor taag white","58-20",2500,4),
("saudi qoor taag white","60-22",2500,1),
("saudi qoor taag white tush","54-22",2500,2),
("saudi qoor taag white tush","54-24",2500,1),
("saudi qoor taag white tush","58-20",2500,3),
("saudi qoor taag white tush","58-22",2500,2),
("saudi qoor taag white tush","60-20",2500,4),
("saudi qoor taag zeitun","54-22",2500,1),
("saudi qoor taag. cream tush","60-22",2500,1),
("saudi qoor tag white tush","54-22",2500,1),
("saudi tush white","60-20",3000,3),
("saudi tush white","60-22",3000,5),
("saudi tush white","60-24",3000,1),
]


class Command(BaseCommand):
    help = "Load the full kanzu/thobe inventory"

    def handle(self, *args, **opts):
        merged = defaultdict(lambda: [0, 0])  # (name, size) -> [qty, price]
        for name, size, price, qty in DATA:
            merged[(name, size)][0] += qty
            merged[(name, size)][1] = price
        created = pieces = skipped = 0
        for (name, size), (qty, price) in sorted(merged.items()):
            _, was_created = Product.objects.get_or_create(
                name=name, size=size,
                defaults={"category": "Kanzu / Thobe", "price": price,
                          "stock": qty, "low_at": 1},
            )
            if was_created:
                created += 1
                pieces += qty
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Added {created} kanzu lines ({pieces} pieces). "
            f"Skipped {skipped} that already existed."))
