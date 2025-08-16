from django.db.models import Sum

from .models import Favorite, Ingredient, Recipe, ShoppingCart


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
    qs = (
        Ingredient.objects.filter(recipes__in_carts__user=user)
        .values('name', 'measurement_unit')
        .annotate(total=Sum('recipeingredient__amount'))
        .order_by('name')
    )
    return [
        f"{i['name']} ({i['measurement_unit']}) — {i['total']}"
        for i in qs
    ]
