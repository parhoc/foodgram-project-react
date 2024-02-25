from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_username
from foodgram_backend import constants


class CustomUser(AbstractUser):
    """
    Custom user model.

    Inherits all fields from AbstractUser except:
    * email Char(254);
    * username Char(150);
    * first_name Char(150);
    * last_name Char(150).
    """

    email = models.EmailField(
        max_length=constants.EMAIL_MAX_LENGTH,
        verbose_name='Электронная почта',
        unique=True
    )
    first_name = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        verbose_name='Фамилия',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )

    def clean(self) -> None:
        validate_username(self.username)
        super().clean()


class Subscription(models.Model):
    """
    User subscription model.

    Fields:
    * user (Int) - FK to user, cascade on delete;
    * subscription (Int) - FK to other user, cascade on delete.

    User and subscription pair must be unique.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    subscription = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписки'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='unique_user_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscription')),
                name='self_subscription'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = (
            'user',
        )

    def __str__(self):
        return f'{self.user} -> {self.subscription}'

    def clean(self) -> None:
        if self.user == self.subscription:
            raise ValidationError(constants.SELF_SUBSCRIPTION_MESSAGE)
