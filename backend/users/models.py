from django.contrib.auth.models import AbstractUser
from django.db import models


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
        max_length=254,
        verbose_name='Электронная почта',
        unique=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )
