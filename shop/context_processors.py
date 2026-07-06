def roles(request):
    user = request.user
    if not user.is_authenticated:
        return {"is_shopkeeper": False, "is_admin": False}
    return {
        "is_admin": user.is_superuser,
        "is_shopkeeper": user.is_superuser
        or user.groups.filter(name="Shopkeeper").exists(),
    }
