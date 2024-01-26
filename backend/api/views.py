from django.contrib.auth import get_user_model
from django.http import Http404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeSubscriptionSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    ShoppingCart,
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

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
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

    @action(
        ['post'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_subscription(self, user, subscription):
        data = {
            'user': user.pk,
            'subscription': subscription.pk,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy_subscription(self, user, subscription):
        try:
            instance = user.subscriptions.get(subscription=subscription)
        except Subscription.DoesNotExist:
            return Response(
                {'errors': 'Subscription does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        subscription = self.get_object()
        if request.method == 'POST':
            return self.create_subscription(request.user, subscription)
        if request.method == 'DELETE':
            return self.destroy_subscription(request.user, subscription)


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
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminOrReadOnly,
    )

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        if self.action == 'shopping_cart':
            return RecipeSubscriptionSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_shopping_cart(self, recipe, user):
        shopping_cart, _ = ShoppingCart.objects.get_or_create(
            user=user,
            defaults={'user': user}
        )
        if shopping_cart.recipes.filter(pk=recipe.pk).exists():
            return Response(
                {'errors': 'Recipe already in the cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.recipes.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_shopping_cart(self, recipe, user):
        try:
            shopping_cart = user.shoppingcart
            shopping_cart.recipes.remove(recipe)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Recipe is not in the shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        try:
            recipe = self.get_object()
        except Http404:
            return Response(
                {'errors': 'Recipe does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            return self.add_to_shopping_cart(recipe, request.user)
        if request.method == 'DELETE':
            return self.remove_from_shopping_cart(recipe, request.user)
