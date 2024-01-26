from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .fields import Base64ImageField
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscription,
    Tag
)

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscriptions.filter(subscription=obj).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'id',
            'name',
            'color'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    measurement_unit = serializers.SerializerMethodField(read_only=True)

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
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True
    )
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                return user.shoppingcart.recipes.filter(pk=obj).exists()
            except User.shoppingcart.RelatedObjectDoesNotExist:
                return False
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_recipe in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_recipe['id'],
                amount=ingredient_recipe['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_recipe in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_recipe['id'],
                amount=ingredient_recipe['amount']
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            context=self.context).to_representation(instance)


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSubscriberSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeSubscriptionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = (
            'user',
            'subscription',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscription')
            ),
        ]

    def validate_subscription(self, value):
        """
        Validate that `user` is not equal to `subscription`.
        """
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                "User can't subscribe to themself."
            )
        return value

    def to_representation(self, instance):
        return UserSubscriberSerializer(
            context=self.context).to_representation(instance.subscription)
