from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'

router_recipes = SimpleRouter()

router_recipes.register(
    r'tags',
    TagViewSet,
    basename='tags'
)

router_recipes.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

router_recipes.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('', include(router_recipes.urls)),
]
