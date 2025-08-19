from django.db.models import F, Sum

from .models import Recipe, RecipeIngredient


def add_to_favorite(user, recipe: Recipe) -> bool:
    obj, created = user.favorites.get_or_create(recipe=recipe)
    return created


def remove_from_favorite(user, recipe: Recipe) -> bool:
    deleted, _ = user.favorites.filter(recipe=recipe).delete()
    return bool(deleted)


def add_to_cart(user, recipe: Recipe) -> bool:
    obj, created = user.shopping_cart.get_or_create(recipe=recipe)
    return created


def remove_from_cart(user, recipe: Recipe) -> bool:
    deleted, _ = user.shopping_cart.filter(recipe=recipe).delete()
    return bool(deleted)


def aggregate_shopping_list(user):
    """Суммирует одинаковые ингредиенты (по имени и ед. изм.)
    """
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
