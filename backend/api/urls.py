from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CustomUserViewSet

app_name = 'api-v1'

router_v1 = SimpleRouter()

router_v1.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
