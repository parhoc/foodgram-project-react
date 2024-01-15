from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
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
        unique=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )
