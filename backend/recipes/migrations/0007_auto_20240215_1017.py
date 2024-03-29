# Generated by Django 3.2 on 2024-02-15 10:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipeingredient_unique_recipe_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Время приготовления должно быть не меньше 1')], verbose_name='Время приготовления, мин'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Количество должно быть не меньше 1')], verbose_name='Количество'),
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
