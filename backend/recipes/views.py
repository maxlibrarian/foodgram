from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAuthorOrReadOnly

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, ShortLink, Tag
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeListSerializer, RecipeMinifiedSerializer,
                          TagSerializer)
from .services import (add_to_cart, add_to_favorite, aggregate_shopping_list,
                       remove_from_cart, remove_from_favorite)


# ReadOnly на дженериках
class TagListView(generics.ListAPIView):
    """
    Возвращает список всех тегов.
    Используется для отображения доступных тегов (например, в фильтрах).
    Не требует аутентификации.
    Пагинация отключена — возвращает все теги сразу.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class TagDetailView(generics.RetrieveAPIView):
    """
    Возвращает детальную информацию о конкретном теге по его ID.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientListView(generics.ListAPIView):
    """
    Возвращает список всех ингредиентов с возможностью поиска по названию.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = IngredientFilter


class IngredientDetailView(generics.RetrieveAPIView):
    """
    Возвращает детальную информацию об ингредиенте
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для рецептов: просмотр, создание, редактирование, удаление.
    """
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'recipeingredient_set__ingredient')
        .all()
    )
    filterset_class = RecipeFilter

    def get_permissions(self):
        """
        Динамически назначает права в зависимости от действия:
        - create: только авторизованный пользователь.
        - partial_update, destroy: авторизованный + проверка авторства.
        - остальные (list, retrieve): разрешено всем.
        """
        if self.action in ('create', 'partial_update', 'destroy'):
            if self.action == 'create':
                return [IsAuthenticated()]
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [AllowAny()]

    def get_serializer_class(self):
        """
        Использует разные сериализаторы:
        - RecipeListSerializer — для списка и деталей.
        - RecipeCreateUpdateSerializer — для создания и редактирования.
        """
        return (
            RecipeListSerializer if self.action in ('list', 'retrieve')
            else RecipeCreateUpdateSerializer
        )

    @staticmethod
    def _build_short_link(request, code: str) -> str:
        """Строит полную короткую ссылку."""

        base = request.build_absolute_uri('/')[:-1]
        return f"{base}/s/{code}"

    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""

        import secrets
        recipe = self.get_object()
        link, _ = ShortLink.objects.get_or_create(
            recipe=recipe, defaults={'code': secrets.token_urlsafe(3)}
        )
        return Response(
            {'short-link': self._build_short_link(request, link.code)}
        )


class FavoriteView(APIView):
    """
    Управление добавлением/удалением рецепта в избранное.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        created = add_to_favorite(request.user, recipe)
        if not created:
            return Response({'detail': 'Рецепт уже в избранном.'}, status=400)
        return Response(
            RecipeMinifiedSerializer(
                recipe, context={'request': request}
            ).data, status=201
        )

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        removed = remove_from_favorite(request.user, recipe)
        if not removed:
            return Response(
                {'detail': 'Рецепта не было в избранном.'}, status=400
            )
        return Response(status=204)


class ShoppingCartView(APIView):
    """
    Управление списком покупок: добавление и удаление рецептов.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        created = add_to_cart(request.user, recipe)
        if not created:
            return Response({'detail': 'Уже в списке покупок.'}, status=400)
        return Response(
            RecipeMinifiedSerializer(
                recipe, context={'request': request}
            ).data, status=201
        )

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        removed = remove_from_cart(request.user, recipe)
        if not removed:
            return Response(
                {'detail': 'Не было в списке покупок.'}, status=400
            )
        return Response(status=204)


class DownloadShoppingCartView(APIView):
    """
    Скачивание списка покупок в виде текстового файла.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lines = aggregate_shopping_list(request.user)
        content = " ".join(lines) or 'Список пуст'
        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
