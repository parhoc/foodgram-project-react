from django_filters import rest_framework as filters

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeFilter(filters.FilterSet):
    """Filter recipes by tags slug and author."""

    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        field_name='tags__slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shoppingcart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def include_filter(self, queryset, value, model):
        user = getattr(self.request, 'user', None)
        filter_queryset = model.objects.filter(user=user).values_list(
            'recipe__pk',
            flat=True
        )
        if value:
            return queryset.filter(pk__in=filter_queryset)
        return queryset.exclude(pk__in=filter_queryset)

    def filter_favorite(self, queryset, name, value):
        return self.include_filter(queryset, value, Favorite)

    def filter_shoppingcart(self, queryset, name, value):
        return self.include_filter(queryset, value, ShoppingCart)


class IngredientFilter(filters.FilterSet):
    """Filter ingredients by name."""

    name = filters.CharFilter(
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
