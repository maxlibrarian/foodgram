from api.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        qs = obj.recipes.all()
        if request:
            limit = request.query_params.get('recipes_limit')
            try:
                if limit is not None:
                    limit_int = int(limit)
                    if limit_int >= 0:
                        qs = qs[:limit_int]
            except (TypeError, ValueError):
                pass
        return RecipeMinifiedSerializer(
            qs, many=True, context=self.context
        ).data


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()
