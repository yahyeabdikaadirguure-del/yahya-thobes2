from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "size", "price", "stock", "low_at", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "image":
                field.widget.attrs.setdefault("class", "input")


class SaleForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(stock__gt=0),
        empty_label="Choose a product…",
    )
    qty = forms.IntegerField(min_value=1, initial=1, label="Quantity")
    sale_date = forms.DateField(
        required=False, label="Date of sale",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    selling_price = forms.DecimalField(
        min_value=0, max_digits=10, decimal_places=2, required=False,
        label="Selling price (KSh)",
    )
    note = forms.CharField(max_length=200, required=False,
                           label="Note (optional — e.g. customer name)")

    def __init__(self, *args, is_manager=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_manager = is_manager
        if is_manager:
            # Managers see the list price and stock as reference;
            # leaving selling price blank uses the list price.
            self.fields["product"].label_from_instance = (
                lambda p: f"{p} — KSh {p.price} — {p.stock} in stock"
            )
            self.fields["selling_price"].help_text = "Leave blank to use the list price."
        else:
            # Cashiers see product names only — no cost, no stock counts —
            # and must enter the price the item actually sold for.
            self.fields["product"].label_from_instance = lambda p: str(p)
            self.fields["selling_price"].required = True
            self.fields.pop("sale_date", None)  # cashiers cannot backdate
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        qty = cleaned.get("qty")
        if product and qty and qty > product.stock:
            if self.is_manager:
                self.add_error("qty", f"Only {product.stock} in stock.")
            else:
                self.add_error("qty", "Not enough of this item available.")
        return cleaned


class StaffForm(forms.Form):
    ROLE_CHOICES = [("Cashier", "Cashier"), ("Shopkeeper", "Shopkeeper")]
    username = forms.CharField(max_length=50)
    password = forms.CharField(min_length=4, widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")
