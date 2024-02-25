from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin model."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    list_filter = (
        'color',
    )
    search_fields = (
        'name',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingredient admin model."""

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name',
    )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe admin model."""

    list_display = (
        'name',
        'author',
        'favorites_count',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    search_fields = (
        'name',
    )
    filter_horizontal = (
        'tags',
    )
    inlines = (
        RecipeIngredientInline,
    )
    readonly_fields = (
        'favorites_count',
    )

    @admin.display(description='Избранное')
    def favorites_count(self, instance):
        return instance.favorings.count()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """RecipeIngredient admin model."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = (
        'recipe',
        'ingredient'
    )
    search_fields = (
        'recipe',
        'ingredient'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ShoppingCart admin model."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorites admin model."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )


admin.site.empty_value_display = 'Не задано'
admin.site.site_title = 'Администирирование Фудграм'
admin.site.site_header = 'Администирирование Фудграм'
