from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import SubscriptionSerializer
from foodgram_backend import constants
from users.models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    User model ViewSet.

    Include create, list and retrive generic methods.

    Methods
    -------
    subscriptions
        Current user subscriptions.
    subscribe
        Add or remove subscription to specified user.
    """

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
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={
                'request': request,
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        ['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """
        Create or delete subscription for current user to specified user.

        Post and delete method. Availible only to authenticated users.
        """
        subscription = self.get_object()
        serializer = SubscriptionSerializer(
            data={
                'user': request.user.pk,
                'subscription': subscription.pk,
            },
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, id):
        subscription = self.get_object()
        try:
            instance = request.user.subscriptions.get(
                subscription=subscription)
        except Subscription.DoesNotExist:
            return Response(
                {'errors': constants.SUBSCRIPTION_DOES_NOT_EXIST},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
