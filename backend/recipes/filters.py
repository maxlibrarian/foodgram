import django_filters as df

from .models import Ingredient, Recipe, Tag


class RecipeFilter(df.FilterSet):
    is_favorited = df.NumberFilter(method='filter_bool')
    is_in_shopping_cart = df.NumberFilter(method='filter_bool')
    author = df.NumberFilter(field_name='author__id')
    tags = df.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all(),
        method='filter_tags_any'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_tags_any(self, queryset, name, value):
        slugs = list(value.values_list('slug', flat=True))
        if not slugs:
            return queryset
        return queryset.filter(tags__slug__in=slugs).distinct()

    def filter_bool(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return queryset.none() if int(value) == 1 else queryset
        if name == 'is_favorited':
            qs = queryset.filter(in_favorites__user=user)
        else:
            qs = queryset.filter(in_carts__user=user)
        if int(value) == 1:
            return qs
        return queryset.exclude(id__in=qs.values('id'))


class IngredientFilter(df.FilterSet):
    name = df.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
