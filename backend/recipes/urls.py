from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DownloadShoppingCartView,
    FavoriteView,
    IngredientDetailView,
    IngredientListView,
    RecipeViewSet,
    ShoppingCartView,
    TagDetailView,
    TagListView,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('tags/', TagListView.as_view(), name='tags-list'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tags-detail'),
    path(
        'ingredients/',
        IngredientListView.as_view(),
        name='ingredients-list'
    ),
    path(
        'ingredients/<int:pk>/',
        IngredientDetailView.as_view(),
        name='ingredients-detail'
    ),
    path(
        'recipes/<int:pk>/favorite/',
        FavoriteView.as_view(),
        name='recipe-favorite'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='recipe-cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download-cart'
    ),
    path(
        'recipes/<int:pk>/get-link/',
        RecipeViewSet.as_view({'get': 'get_link'}),
        name='recipe-get-link'
    ),
]

urlpatterns += router.urls
