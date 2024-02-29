from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .fields import ImageFieldURL
from foodgram_backend import constants
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """
    Tag model serializer.

    Include fields:
    * id (read only);
    * name;
    * color;
    * slug.
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'name',
            'color'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Ingredient model serializer.

    Include fields:
    * id (read only);
    * name;
    * measurement_unit.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class LimitedListSerializer(serializers.ListSerializer):
    """
    ListSerializer with limited number of return values.

    Number of return values limited by `recipe_limit` query parameter.
    """

    def to_representation(self, data):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                data = data.all()[:recipes_limit]
            except ValueError:
                pass
        return super().to_representation(data)


class RecipeSimpleSerializer(serializers.ModelSerializer):
    """
    Recipe model serializer with fewer fields.

    Include fields:
    * id (read only);
    * name;
    * image;
    * cooking_time.
    """

    image = ImageFieldURL()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        list_serializer_class = LimitedListSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    RecipeIngredient model serializer.

    Include fields:
    * id (read only) - ingredient id;
    * name - ingredient name;
    * measurement_unit - ingredient measurement unit;
    * amount.
    """

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_id(self, obj):
        return IngredientSerializer(obj.ingredient).data['id']

    def get_name(self, obj):
        return IngredientSerializer(obj.ingredient).data['name']

    def get_measurement_unit(self, obj):
        return IngredientSerializer(obj.ingredient).data['measurement_unit']


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    RecipeIngredient model create serializer.

    Include fields:
    * id (read only) - ingredient id;
    * amount.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Recipe model serializer.

    Include fields:
    * id (read only);
    * tags - `TagSerializer`, many;
    * author (read only);
    * ingredients - `RecipeIngredientSerializer`, many;
    * is_favorited (read only) - custom field, if specified recipe in
    user's favorites;
    * is_in_shopping_cart (read only) - custom field, if specified recipe in
    user's shopping cart;
    * name;
    * image - coded in base64;
    * text;
    * cooking_time.
    """

    from api.users.serializers import CustomUserSerializer

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True
    )
    image = ImageFieldURL()
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def _is_in(self, obj, model) -> bool:
        """
        Checks if `obj` in `model` for current user.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return model.objects.filter(user=user.pk, recipe=obj.pk).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        return self._is_in(obj, ShoppingCart)

    def get_is_favorited(self, obj):
        return self._is_in(obj, Favorite)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Recipe model create serializer.

    Include fields:
    * ingredients - `RecipeIngredientSerializer`, many;
    * tags - `TagSerializer`, many;
    * image - coded in base64;
    * name;
    * text;
    * cooking_time.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        source='recipeingredient_set'
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create_recipe_ingredients(self, recipe, ingredients):
        """Creates records in RecipeIngredient table."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_recipe['id'],
                amount=ingredient_recipe['amount']
            )
            for ingredient_recipe in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_recipe_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            context=self.context).to_representation(instance)

    def validate_ingredients(self, value):
        ingredients = set(ingredisnt.get('id') for ingredisnt in value)
        if len(set(ingredients)) != len(value):
            error_msg = {'error': constants.INGREDIENTS_UNIQUE_ERROR}
            raise serializers.ValidationError(error_msg)
        return value


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    ShoppingCart model serializer.

    Include fields:
    * user;
    * recipe.

    User and recipe pair must be unique.
    """

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            ),
        ]

    def to_representation(self, instance):
        return RecipeSimpleSerializer(
            context=self.context).to_representation(instance.recipe)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    ShoppingCart model serializer.

    Include fields:
    * user;
    * recipe.

    User and recipe pair must be unique.
    """

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            ),
        ]

    def to_representation(self, instance):
        return RecipeSimpleSerializer(
            context=self.context).to_representation(instance.recipe)
