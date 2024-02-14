import re

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Recipe tag model.

    Fields:
    * name (Char(200));
    * color (Char(7)) - tag hex color mark;
    * slug (Slug).
    """

    HEX_COLOR_REGEX = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        validators=(
            RegexValidator(HEX_COLOR_REGEX),
        )
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = (
            'name',
        )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """
    Recipe ingredient model.

    Fields:
    * name (Char(200));
    * measurement_unit (Char(200)).
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = (
            'name',
        )

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Recipe model.

    Fields:
    * name (Char(200));
    * text (Text) - recipe description;
    * ingredients - ManyToMany connection to Ingredient model;
    * tags - ManyToMany connection to Tag model;
    * image (Image);
    * cooking_time (Int);
    * author (Int) - FK to User model, cascade on delete;
    * pub_date (DateTime) - Recipe creation date, auto now.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиетны',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления, мин',
        validators=(
            MinValueValidator(1),
        )
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = (
            '-pub_date',
        )

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """
    ManyToMany support model for Recipe and Ingredient models.

    Fields:
    * recipe (Int) - FK to Recipe model, cascade on delete;
    * ingredient (Int) - FK to Ingredient model, cascade on delete;
    * amount (Int) - ingredient amount in recipe, minimum 1.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(1),
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Рецепт и ингредиент'
        verbose_name_plural = 'Рецепты и ингредиенты'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Subscription(models.Model):
    """
    User subscription model.

    Fields:
    * user (Int) - FK to user, cascade on delete;
    * subscription (Int) - FK to other user, cascade on delete.

    User and subscription pair must be unique.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписки'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='unique_user_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = (
            'user',
        )

    def __str__(self):
        return f'{self.user.username} -> {self.subscription.username}'


class ShoppingCart(models.Model):
    """
    Shopping cart model.

    Fields:
    * user (Int) - FK to User, cascade on delete;
    * recipe (Int) - FK to Recipe, cascade on delete.

    User and recipe pair must be unique.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingusers',
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = (
            'user',
        )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username}: {self.recipe.name}'


class Favorite(models.Model):
    """
    Favorite user recipes model.

    Fields:
    * user (Int) - FK to User, cascade on delete;
    * recipe (Int) - FK to Recipe, cascade on delete.

    User and recipe pair must be unique.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorings',
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = (
            'user',
        )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username}: {self.recipe.name}'
