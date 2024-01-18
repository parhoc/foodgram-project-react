from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    TagSerializer
)
from recipes.models import (
    Ingredient,
    Tag,
)

User = get_user_model()


class CustomUserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_instance(self):
        return self.request.user

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
