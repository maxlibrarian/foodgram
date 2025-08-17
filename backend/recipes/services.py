from django.db.models import Sum, F

from .models import Favorite, Recipe, ShoppingCart


def add_to_favorite(user, recipe: Recipe) -> bool:
    obj, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
    return created


def remove_from_favorite(user, recipe: Recipe) -> bool:
    deleted, _ = Favorite.objects.filter(user=user, recipe=recipe).delete()
    return bool(deleted)


def add_to_cart(user, recipe: Recipe) -> bool:
    obj, created = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
    return created


def remove_from_cart(user, recipe: Recipe) -> bool:
    deleted, _ = ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
    return bool(deleted)


def aggregate_shopping_list(user):
    """Суммирует одинаковые ингредиенты (по имени и ед. изм.)
    """
    from .models import RecipeIngredient
    qs = (
        RecipeIngredient.objects
        .filter(recipe__in_carts__user=user)
        .values(
            name=F('ingredient__name'), unit=F('ingredient__measurement_unit')
        )
        .annotate(total=Sum('amount'))
        .order_by('name')
    )
    return [f"{row['name']} ({row['unit']}) — {row['total']}" for row in qs]
