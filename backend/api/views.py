from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag,
)

User = get_user_model()


class CustomUserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return SubscriptionSerializer
        return CustomUserSerializer

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(['get'], detail=False)
    def subscriptions(self, request):
        queryset = request.user.subscriptions.all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            many=True,
            context={
                'request': request,
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(['post'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_subscription(self, user, subscription):
        get_object_or_404(User, pk=subscription)
        data = {
            'user': user,
            'subscription': subscription,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy_subscription(self, subscription):
        user = self.get_object()
        try:
            instance = user.subscribers.get(subscription=subscription)
        except Subscription.DoesNotExist:
            return Response(
                {'errors': 'Subscription does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, pk):
        if request.method == 'POST':
            return self.create_subscription(request.user.pk, pk)
        if request.method == 'DELETE':
            return self.destroy_subscription(pk)


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
        'trace'
    ]

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
