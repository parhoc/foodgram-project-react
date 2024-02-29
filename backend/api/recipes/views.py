from django.db.models import F, Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import PartialUpdateMixin
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from api import utils
from api.permissions import IsAuthorAdminOrReadOnly
from foodgram_backend import constants
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tag model ViewSet.

    Include only list and retrive methods.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
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


class RecipeViewSet(PartialUpdateMixin, viewsets.ModelViewSet):
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

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminOrReadOnly,
    )
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def error_message(self, model):
        """Construct remove from model error message."""
        class_name = utils.class_name(model.__name__)
        return constants.REMOVE_ERROR_MESSAGE.format(class_name)

    def add_to(self, user, recipe_pk):
        """Add new record to model based on method serializer."""
        serializer = self.serializer_class(
            data={
                'user': user.pk,
                'recipe': recipe_pk,
            },
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

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
        ['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk):
        """
        Add or remove recipe from current user shopping cart.

        Post and delete method. Availible only to authenticated users.
        """
        return self.add_to(request.user, pk)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        return self.remove_from(request.user, ShoppingCart)

    @action(
        ['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        """
        Add or remove recipe from current user favorites.

        Post and delete method. Availible only to authenticated users.
        """
        return self.add_to(request.user, pk)

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk):
        return self.remove_from(request.user, Favorite)

    def get_ingredients(self):
        """
        Return shopping cart recipes ingredients as dictionary.

        Sum amounts of the same ingredients.
        """
        ingredients_sum = RecipeIngredient.objects.filter(
            recipe__in=self.request.user.shoppingcart.values_list(
                'recipe__pk',
                flat=True
            )
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(
            amount_sum=Sum('amount')
        )
        return ingredients_sum

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
            pdf_buffer, as_attachment=True, filename='shoppinglist.pdf'
        )
