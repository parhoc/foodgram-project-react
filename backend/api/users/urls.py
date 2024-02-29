from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CustomUserViewSet

app_name = 'users'

router_users = SimpleRouter()

router_users.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_users.urls)),
]
