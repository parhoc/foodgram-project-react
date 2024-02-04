from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import utils
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscription,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class CustomUserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    User model ViewSet.

    Include create, list and retrive generic methods.

    Methods
    -------
    me
        Reference to current user.
    subscriptions
        Current user subscriptions.
    set_password
        Change current user password.
    subscribe
        Add or remove subscription to specified user.
    """

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
        """
        Return response with current authenticated user details.

        Get method. Availible only to authenticated users.
        """
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """
        Return response with current authenticated user subscriptions.

        Get method. Availible only to authenticated users.
        """
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
        """
        Change current authenticated user password.

        Post method. Availible only to authenticated users.
        """
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
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        """
        Create or delete subscription for current user to specified user.

        Post and delete method. Availible only to authenticated users.
        """
        subscription = self.get_object()
        if request.method == 'POST':
            return self.create_subscription(request.user, subscription)
        if request.method == 'DELETE':
            return self.destroy_subscription(request.user, subscription)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    Tag model ViewSet.

    Include only list and retrive methods.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Ingredient model ViewSet.

    Include only list and retrive methods.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Recipe model ViewSet.

    Accept all http methods except Put.

    Methods
    -------
    shopping_cart
        Add or remove recipe from shopping cart.
    favorite
        Add or remove recipe from favorites cart.
    download_shopping_cart
        Download recipes ingredients in shopping cart as PDF.
    """

    REMOVE_ERROR_MESSAGE = 'Recipe is not in the {}.'
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
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = RecipeFilter

    def filter_queryset_param(self, queryset, query_param, model):
        """
        Filter given `queryset` from `model` based on `query_param` value.

        `query_param` can be '1' - include or '0' - exclude records from
        `queryset` that exist in given `model`.
        """
        user = self.request.user
        filter_queryset = model.objects.filter(user=user).values_list(
            'recipe__pk',
            flat=True
        )
        if query_param == '1':
            queryset = queryset.filter(pk__in=filter_queryset)
        elif query_param == '0':
            queryset = queryset.exclude(pk__in=filter_queryset)
        return queryset

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None:
            queryset = self.filter_queryset_param(
                queryset,
                is_favorited,
                Favorite
            )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None:
            queryset = self.filter_queryset_param(
                queryset,
                is_in_shopping_cart,
                ShoppingCart
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def error_message(self, model):
        """Construct remove from model error message."""
        class_name = utils.class_name(model.__name__)
        return self.REMOVE_ERROR_MESSAGE.format(class_name)

    def add_to(self, user):
        """Add new record to model based on method serializer."""
        try:
            recipe = self.get_object()
        except Http404:
            return Response(
                {'errors': 'Recipe does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'user': user.pk,
            'recipe': recipe.pk,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def remove_from(self, user, model):
        """Remove record from given model."""
        recipe = self.get_object()
        try:
            instance = model.objects.get(user=user.pk, recipe=recipe.pk)
        except model.DoesNotExist:
            return Response(
                {'errors': self.error_message(model)},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """
        Add or remove recipe from current user shopping cart.

        Post and delete method. Availible only to authenticated users.
        """
        if request.method == 'POST':
            return self.add_to(request.user)
        if request.method == 'DELETE':
            return self.remove_from(request.user, ShoppingCart)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """
        Add or remove recipe from current user favorites.

        Post and delete method. Availible only to authenticated users.
        """
        if request.method == 'POST':
            return self.add_to(request.user)
        if request.method == 'DELETE':
            return self.remove_from(request.user, Favorite)

    def get_ingredients(self):
        """
        Return shopping cart recipes ingredients as dictionary.

        Summ amounts of the same ingredients.
        """
        recipes = self.request.user.shoppingcart.values_list(
            'recipe__pk',
            flat=True
        )
        ingredients_amount = RecipeIngredient.objects.filter(
            recipe__in=recipes).all()
        ingredients = dict()
        for ingredient in ingredients_amount:
            pk = ingredient.ingredient.pk
            if pk in ingredients:
                ingredients[pk]['amount'] += ingredient.amount
            else:
                ingredients[pk] = {
                    'name': ingredient.ingredient.name,
                    'amount': ingredient.amount,
                    'measurement_unit': ingredient.ingredient.measurement_unit,
                }
        return ingredients

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Return PDF file with shopping cart recipes ingredients.

        Get method. Availible only to authenticated users.
        """
        ingredients = self.get_ingredients()
        pdf_buffer = utils.get_pdf(ingredients)
        return FileResponse(
            pdf_buffer, as_attachment=True, filename='shoppinglist.pdf')
