from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        field_name='tags__slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )
