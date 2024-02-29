from django.urls import include, path

app_name = 'api-v1'

urlpatterns = [
    path('', include('api.recipes.urls')),
    path('', include('api.users.urls')),
]
