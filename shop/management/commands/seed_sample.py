"""Load the sample thobe and men's wear inventory:
    python manage.py seed_sample
"""
from django.core.management.base import BaseCommand

from shop.models import Product

SAMPLE = [
    ("Emirati Kanzu, White", "Kanzu / Thobe", "M", 2800, 12, 3),
    ("Emirati Kanzu, White", "Kanzu / Thobe", "L", 2800, 9, 3),
    ("Emirati Kanzu, White", "Kanzu / Thobe", "XL", 3000, 6, 3),
    ("Saudi Thobe, White collar", "Kanzu / Thobe", "L", 3200, 8, 3),
    ("Saudi Thobe, White collar", "Kanzu / Thobe", "XL", 3400, 5, 3),
    ("Moroccan Thobe, Beige", "Kanzu / Thobe", "L", 3800, 4, 3),
    ("Omani Kanzu with tassel", "Kanzu / Thobe", "M", 2600, 10, 3),
    ("Black Thobe, gold embroidery", "Kanzu / Thobe", "L", 4500, 3, 2),
    ("Men's Jalabiya, Grey", "Jalabiya", "L", 2200, 7, 3),
    ("Bisht (men's cloak), Black-gold", "Kanzu / Thobe", "Free size", 8500, 2, 1),
    ("Kufi cap, White crochet", "Men's Accessories", "Free size", 350, 30, 8),
    ("Barghashia cap, Embroidered", "Men's Accessories", "Free size", 650, 15, 5),
    ("Shemagh scarf, Red-white", "Men's Accessories", "Free size", 800, 14, 5),
    ("Tasbih prayer beads", "Prayer Wear", "-", 250, 40, 10),
    ("Men's prayer mat, Padded", "Prayer Wear", "-", 1200, 11, 4),
    ("Boys' Kanzu, White", "Kids", "Kids", 1500, 8, 3),
]


class Command(BaseCommand):
    help = "Load a sample thobe & men's wear inventory"

    def handle(self, *args, **options):
        created = 0
        for name, category, size, price, stock, low_at in SAMPLE:
            _, was_created = Product.objects.get_or_create(
                name=name, size=size,
                defaults={"category": category, "price": price,
                          "stock": stock, "low_at": low_at},
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Added {created} sample products."))
