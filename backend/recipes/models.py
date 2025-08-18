from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from . import constants as c

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов рецептов."""

    name = models.CharField(
        max_length=32, unique=True, verbose_name='Название'
    )
    slug = models.SlugField(max_length=32, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['slug']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов рецептов."""

    name = models.CharField(max_length=128, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=64, verbose_name='Ед. измерения'
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель, описывающая рецепты."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор'
    )
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=[
            MinValueValidator(
                c.MIN_COOKING_TIME,
                f'Минимальное время - {c.MIN_COOKING_TIME} минута.'
            ),
            MaxValueValidator(
                c.MAX_COOKING_TIME,
                f'Максимальное время - {c.MAX_COOKING_TIME} минут.'
            )
        ]
    )
    tags = models.ManyToManyField(
        'Tag', through='RecipeTag', related_name='recipes', verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient',
        related_name='recipes', verbose_name='Ингредиенты'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная модель тэгов-рецептов."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тег')

    class Meta:
        unique_together = ('recipe', 'tag')
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ['-id']

    def __str__(self):
        return self.recipe


class RecipeIngredient(models.Model):
    """Промежуточная модель игредиентов-рецептов."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт', related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент', related_name='ingredient_in_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                c.MIN_INGREDIENT_AMOUNT,
                f'Минимальное количество - {c.MIN_INGREDIENT_AMOUNT}'
            ),
            MaxValueValidator(
                c.MAX_INGREDIENT_AMOUNT,
                f'Максимальное количество - {c.MAX_INGREDIENT_AMOUNT}'
            )
        ]
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ['-recipe']

    def __str__(self):
        return self.recipe


class Favorite(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_favorites', verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.user


class ShoppingCart(models.Model):
    """Модель для продуктовой корзины."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_carts', verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Элемент списка покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ['-recipe']

    def __str__(self):
        return self.recipe


class ShortLink(models.Model):
    """Модель для коротких ссылок."""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE,
        related_name='short_link', verbose_name='Рецепт'
    )
    code = models.CharField(max_length=16, unique=True, verbose_name='Код')

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ['-recipe']

    def __str__(self):
        return self.code
