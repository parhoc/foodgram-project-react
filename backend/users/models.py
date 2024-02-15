from django.contrib.auth.models import AbstractUser
from django.db import models
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
    username = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        verbose_name='Логин',
        unique=True,
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
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__in=constants.INVALID_USERNAMES),
                name='invalid_username'
            ),
        ]
