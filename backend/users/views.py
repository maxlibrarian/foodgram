from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from http import HTTPStatus

from .models import Subscription
from .serializers import (
    SetAvatarSerializer,
    SetPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)

User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет для управления пользователями.

    Поддерживает:
    - Регистрация нового пользователя (POST)
    - Просмотр списка пользователей (GET)
    - Просмотр профиля конкретного пользователя (GET)
    - Кастомные действия:
        - /me — текущий пользователь
        - /set_password — смена пароля
        - /me/avatar — управление аватаром
        - /subscriptions — список подписок
        - /{id}/subscribe — подписка/отписка

    Использует разные сериализаторы для создания и чтения.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        return (
            UserCreateSerializer
            if self.action == 'create' else UserSerializer
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return Response(
            UserSerializer(request.user, context={'request': request}).data
        )

    @action(
        detail=False, methods=['post'],
        permission_classes=[IsAuthenticated], url_path='set_password'
    )
    def set_password(self, request):
        ser = SetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if not request.user.check_password(
            ser.validated_data['current_password']
        ):
            return Response(
                {'current_password': ['Неверный пароль.']},
                status=HTTPStatus.BAD_REQUEST
            )
        request.user.set_password(ser.validated_data['new_password'])
        request.user.save()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False, methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def set_avatar(self, request):
        ser = SetAvatarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        request.user.avatar = ser.validated_data['avatar']
        request.user.save()
        return Response(
            {'avatar': request.build_absolute_uri(request.user.avatar.url)},
            status=HTTPStatus.OK
        )

    @set_avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=True)
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user).distinct()
        page = self.paginate_queryset(authors)
        ser = UserWithRecipesSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(ser.data)

    @action(
        detail=True, methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if author == request.user:
            return Response(
                {'detail': 'Нельзя подписаться на себя.'},
                status=HTTPStatus.BAD_REQUEST
            )
        obj, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )
        if not created:
            return Response(
                {'detail': 'Уже подписаны.'},
                status=HTTPStatus.BAD_REQUEST
            )
        data = UserWithRecipesSerializer(
            author, context={'request': request}
        ).data
        return Response(data, status=HTTPStatus.CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        deleted, _ = request.user.following.filter(author=author).delete()
        if not deleted:
            return Response(
                {'detail': 'Подписки не было.'},
                status=HTTPStatus.BAD_REQUEST
            )
        return Response(status=HTTPStatus.NO_CONTENT)
