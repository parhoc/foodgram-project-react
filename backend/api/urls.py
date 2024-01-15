from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet

app_name = 'api-v1'

router_v1 = SimpleRouter()

router_v1.register(
    r'users',
    UserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router_v1.urls)),
]
