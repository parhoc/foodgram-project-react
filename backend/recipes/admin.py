from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscription,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'measurement_unit',
    )
    search_fields = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
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
        'ingredients',
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscription',
    )
