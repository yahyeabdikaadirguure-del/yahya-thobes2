from django.conf import settings
from django.db import models

CATEGORY_CHOICES = [(c, c) for c in [
    "Kanzu / Thobe", "Khamis", "Jalabiya", "Shaal", "Cimaamad",
    "Sali", "Kofiyado", "Tusbah", "Perfume", "Watches", "Rings",
    "T-shirts", "Vest", "Surwal", "Men's Accessories", "Kids",
    "Shoes", "Other",
]]

GENERAL_SIZES = ["-", "XS", "S", "M", "L", "XL", "XXL", "Free size"]

# Height sizes (kids thobe & shaal): 20 to 60 in steps of 2
KIDS_SIZES = [str(h) for h in range(20, 61, 2)]

# Men thobe: height-width combinations
_MEN_COMBOS = {
    54: [20, 21, 22, 23, 24, 26],
    55: [20, 21, 22],
    56: [20, 21, 22, 23, 24],
    57: [20, 21, 22, 23, 24],
    58: [20, 21, 22, 23, 24, 25, 26],
    59: [20, 21, 22, 23, 24],
    60: [20, 22, 23, 24, 26, 28],
    62: [22, 23, 24, 26, 28],
}
MEN_SIZES = [f"{h}-{w}" for h, widths in _MEN_COMBOS.items() for w in widths]

SHOE_SIZES = [f"Shoe {n}" for n in range(40, 47)]

SIZE_CHOICES = [
    ("General", [(s, s) for s in GENERAL_SIZES]),
    ("Kids thobe & shaal (height)", [(s, s) for s in KIDS_SIZES]),
    ("Men thobe (height-width)", [(s, s) for s in MEN_SIZES]),
    ("Shoes", [(s, s) for s in SHOE_SIZES]),
]


class Product(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="Kanzu / Thobe")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default="-")
    price = models.DecimalField("Price (KSh)", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    low_at = models.PositiveIntegerField("Alert when stock is at or below", default=3)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "size"]

    @property
    def is_low(self):
        return self.stock <= self.low_at

    def __str__(self):
        return f"{self.name} ({self.size})" if self.size != "-" else self.name


class Sale(models.Model):
    product = models.ForeignKey(
        Product, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="sales",
    )
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="sales_made",
    )
    name_snapshot = models.CharField(max_length=160)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name_snapshot} x {self.qty}"
