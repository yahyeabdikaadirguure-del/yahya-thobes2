import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


def _is_shopkeeper(user):
    return user.is_superuser or user.groups.filter(name="Shopkeeper").exists()


shopkeeper_required = user_passes_test(_is_shopkeeper)
admin_required = user_passes_test(lambda u: u.is_superuser)
from django.db.models import DecimalField, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProductForm, SaleForm
from .models import Product, Sale


def _revenue(qs):
    return qs.aggregate(t=Sum("total"))["t"] or Decimal("0")


def _trend(current, previous):
    if previous and previous > 0:
        return round((current - previous) / previous * 100)
    return None


@login_required
def dashboard(request):
    today = timezone.localdate()
    if not _is_shopkeeper(request.user):
        my_sales = Sale.objects.filter(created_at__date=today, sold_by=request.user)
        return render(request, "shop/dashboard_cashier.html", {
            "tab": "dashboard",
            "my_sales": my_sales,
            "my_total": _revenue(my_sales),
            "my_count": my_sales.count(),
        })
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)
    sales = Sale.objects.all()

    stock_value = Product.objects.aggregate(
        v=Sum(F("price") * F("stock"), output_field=DecimalField())
    )["v"] or 0

    context = {
        "tab": "dashboard",
        "today_total": _revenue(sales.filter(created_at__date=today)),
        "today_count": sales.filter(created_at__date=today).count(),
        "week_total": _revenue(sales.filter(created_at__date__gte=week_start)),
        "month_total": _revenue(sales.filter(created_at__date__gte=month_start)),
        "stock_value": stock_value,
        "product_count": Product.objects.count(),
        "low_stock": Product.objects.filter(stock__lte=F("low_at")),
        "recent_sales": sales.select_related("product")[:10],
    }
    return render(request, "shop/dashboard.html", context)


@login_required
@shopkeeper_required
def insights(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)
    prev_week_start = today - timedelta(days=13)
    prev_month_start = today - timedelta(days=59)

    daily = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily.append({
            "label": day.strftime("%a"),
            "value": float(_revenue(Sale.objects.filter(created_at__date=day))),
        })

    weekly = []
    for w in range(3, -1, -1):
        start = today - timedelta(days=w * 7 + 6)
        end = today - timedelta(days=w * 7)
        weekly.append({
            "label": "This wk" if w == 0 else f"{w} wk ago",
            "value": float(_revenue(Sale.objects.filter(
                created_at__date__gte=start, created_at__date__lte=end
            ))),
        })

    week_total = _revenue(Sale.objects.filter(created_at__date__gte=week_start))
    prev_week_total = _revenue(Sale.objects.filter(
        created_at__date__gte=prev_week_start, created_at__date__lt=week_start
    ))
    month_total = _revenue(Sale.objects.filter(created_at__date__gte=month_start))
    prev_month_total = _revenue(Sale.objects.filter(
        created_at__date__gte=prev_month_start, created_at__date__lt=month_start
    ))

    top_sellers = (
        Sale.objects.filter(created_at__date__gte=month_start)
        .values("name_snapshot")
        .annotate(units=Sum("qty"), revenue=Sum("total"))
        .order_by("-revenue")[:5]
    )

    staff_sales = (
        Sale.objects.filter(created_at__date__gte=month_start, sold_by__isnull=False)
        .values("sold_by__username")
        .annotate(units=Sum("qty"), revenue=Sum("total"))
        .order_by("-revenue")
    )

    context = {
        "tab": "insights",
        "week_total": week_total,
        "week_trend": _trend(week_total, prev_week_total),
        "month_total": month_total,
        "month_trend": _trend(month_total, prev_month_total),
        "daily_json": json.dumps(daily),
        "weekly_json": json.dumps(weekly),
        "top_sellers": top_sellers,
        "staff_sales": staff_sales,
    }
    return render(request, "shop/insights.html", context)


@login_required
def record_sale(request):
    is_manager = _is_shopkeeper(request.user)
    if request.method == "POST":
        form = SaleForm(request.POST, is_manager=is_manager)
        if form.is_valid():
            product = form.cleaned_data["product"]
            qty = form.cleaned_data["qty"]
            price = form.cleaned_data.get("selling_price")
            if price is None:
                price = product.price
            Sale.objects.create(
                product=product,
                sold_by=request.user,
                name_snapshot=str(product),
                qty=qty,
                unit_price=price,
                total=price * qty,
                note=form.cleaned_data.get("note", ""),
            )
            product.stock -= qty
            product.save(update_fields=["stock"])
            messages.success(request, f"Sale recorded: {product} × {qty}.")
            return redirect("record_sale")
    else:
        form = SaleForm(is_manager=is_manager)

    today = timezone.localdate()
    today_sales = Sale.objects.filter(created_at__date=today)
    if not _is_shopkeeper(request.user):
        today_sales = today_sales.filter(sold_by=request.user)
    context = {
        "tab": "sale",
        "form": form,
        "today_sales": today_sales,
        "has_products": Product.objects.exists(),
    }
    return render(request, "shop/sale.html", context)


@login_required
@shopkeeper_required
@require_POST
def undo_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if sale.product:
        sale.product.stock += sale.qty
        sale.product.save(update_fields=["stock"])
    sale.delete()
    messages.success(request, "Sale undone and stock restored.")
    return redirect(request.POST.get("next") or "dashboard")


@login_required
@shopkeeper_required
def inventory(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query) | products.filter(
            category__icontains=query
        )
    context = {"tab": "inventory", "products": products, "query": query}
    return render(request, "shop/inventory.html", context)


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Added {product}.")
            if _is_shopkeeper(request.user):
                return redirect("inventory")
            return redirect("product_create")
    else:
        form = ProductForm()
    tab = "inventory" if _is_shopkeeper(request.user) else "addproduct"
    return render(request, "shop/product_form.html",
                  {"tab": tab, "form": form, "title": "New product"})


@login_required
@shopkeeper_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Saved changes to {product}.")
            return redirect("inventory")
    else:
        form = ProductForm(instance=product)
    return render(request, "shop/product_form.html",
                  {"tab": "inventory", "form": form, "title": "Edit product"})


@require_POST
@login_required
@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = str(product)
    product.delete()
    messages.success(request, f"Deleted {name}.")
    return redirect("inventory")


# ── Staff management (admin only) ────────────────────────────────
from django.contrib.auth.models import Group, User

from .forms import StaffForm


def _role_of(user):
    if user.is_superuser:
        return "Admin"
    if user.groups.filter(name="Shopkeeper").exists():
        return "Shopkeeper"
    if user.groups.filter(name="Cashier").exists():
        return "Cashier"
    return "No role"


@login_required
@admin_required
def staff_list(request):
    staff = [
        {"user": u, "role": _role_of(u)}
        for u in User.objects.all().order_by("username")
    ]
    return render(request, "shop/staff.html",
                  {"tab": "staff", "staff": staff, "form": StaffForm()})


@login_required
@admin_required
def staff_create(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            role = form.cleaned_data["role"]
            user, created = User.objects.get_or_create(username=username)
            user.set_password(form.cleaned_data["password"])
            user.is_superuser = False
            user.is_staff = False
            user.is_active = True
            user.save()
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.clear()
            user.groups.add(group)
            verb = "Added" if created else "Updated"
            messages.success(request, f"{verb} {role.lower()} '{username}'.")
        else:
            for errs in form.errors.values():
                for e in errs:
                    messages.error(request, e)
    return redirect("staff_list")


@login_required
@admin_required
@require_POST
def staff_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    elif user.is_superuser:
        messages.error(request, "Admin accounts cannot be deactivated here.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        state = "activated" if user.is_active else "deactivated"
        messages.success(request, f"'{user.username}' {state}.")
    return redirect("staff_list")
