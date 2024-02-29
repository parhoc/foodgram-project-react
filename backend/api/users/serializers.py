from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend import constants
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    User model serializer.

    Include fields:
    * email;
    * id (read only);
    * username;
    * first_name;
    * last_name;
    * is_subscribed (read only) - custom field, if current user
    subscribed on specified user.
    """

    is_subscribed = serializers.SerializerMethodField()

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
        return (user.is_authenticated
                and user.subscriptions.filter(subscription=obj).exists())


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    User model create serializer.

    Include fields:
    * email;
    * id (read only);
    * username;
    * first_name;
    * last_name;
    * password (write only).
    """

    def validate_username(self, value):
        if value in constants.INVALID_USERNAMES:
            error_msg = {
                'error': constants.INVALID_USERNAME_MESSAGE.format(value),
            }
            raise serializers.ValidationError(error_msg)
        return value


class UserSubscriberSerializer(CustomUserSerializer):
    """
    User model serializer for subscription response.

    Include fields:
    * email;
    * id (read only);
    * username;
    * first_name;
    * last_name;
    * is_subscribed (read only) - custom field, if current user
    subscribed on specified user.
    * recipes (read only) - user recipes, many;
    * recipes_count (read only) - custom field.
    """
    from api.recipes.serializers import RecipeSimpleSerializer

    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSimpleSerializer(
        many=True,
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
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Subscription model serializer.

    Include fields:
    * user;
    * subscription.

    User and subscription pair must be unique.
    """

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
                constants.SELF_SUBSCRIPTION_MESSAGE
            )
        return value

    def to_representation(self, instance):
        return UserSubscriberSerializer(
            context=self.context).to_representation(instance.subscription)
