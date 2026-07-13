from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("insights/", views.insights, name="insights"),
    path("sale/", views.record_sale, name="record_sale"),
    path("sale/<int:pk>/undo/", views.undo_sale, name="undo_sale"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/add/", views.product_create, name="product_create"),
    path("inventory/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("inventory/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.staff_create, name="staff_create"),
    path("staff/<int:pk>/toggle/", views.staff_toggle, name="staff_toggle"),
    path("staff/<int:pk>/delete/", views.staff_delete, name="staff_delete"),
    path("staff/<int:pk>/sales/", views.staff_sales_detail, name="staff_sales"),
]
