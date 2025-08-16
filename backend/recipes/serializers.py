from api.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def _check(self, model, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated:
            return False
        return model.objects.filter(user=user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        from .models import Favorite
        return self._check(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        from .models import ShoppingCart
        return self._check(ShoppingCart, obj)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountWriteSerializer(many=True, write_only=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, write_only=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        errors = {}
        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')

        if not ingredients:
            errors.setdefault('ingredients', []).append('Обязательное поле.')
        else:
            ids = [it['id'] for it in ingredients]
            if len(set(ids)) != len(ids):
                errors.setdefault('ingredients', []).append(
                    'Ингредиенты не должны повторяться.'
                )
            existing_ids = set(
                Ingredient.objects.filter(id__in=ids).values_list(
                    'id', flat=True
                )
            )
            missing = [i for i in ids if i not in existing_ids]
            if missing:
                errors.setdefault('ingredients', []).append(
                    'Некоторые ингредиенты не найдены.'
                )
        if not tags:
            errors.setdefault('tags', []).append('Обязательное поле.')
        else:
            if len(set(tags)) != len(tags):
                errors.setdefault('tags', []).append(
                    'Теги не должны повторяться.'
                )
            existing_tag_ids = set(
                Tag.objects.filter(id__in=tags).values_list(
                    'id', flat=True
                )
            )
            missing_tags = [t for t in tags if t not in existing_tag_ids]
            if missing_tags:
                errors.setdefault('tags', []).append(
                    'Некоторые теги не найдены.'
                )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def _save_m2m(self, recipe, ingredients, tags):
        """
        Хелпер, который синхронизирует связи «многие-ко-многим»
        у рецепта после валидации данных.
        """
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for item in ingredients:
            ingredient = Ingredient.objects.get(pk=item['id'])
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=item['amount']
            )
        RecipeTag.objects.filter(recipe=recipe).delete()
        for tag_id in tags:
            tag = Tag.objects.get(pk=tag_id)
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self._save_m2m(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients is not None:
            self._save_m2m(instance, ingredients, tags or [])
        elif tags is not None:
            self._save_m2m(instance, [], tags)
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data
