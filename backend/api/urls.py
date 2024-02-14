from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from .users.views import CustomUserViewSet

app_name = 'api-v1'

router_v1 = SimpleRouter()

router_v1.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)

router_v1.register(
    r'tags',
    TagViewSet,
    basename='tags'
)

router_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
