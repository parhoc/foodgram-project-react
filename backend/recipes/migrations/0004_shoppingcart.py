# Generated by Django 3.2 on 2024-01-26 10:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_auto_20240125_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(to='recipes.Recipe', verbose_name='Рецепты')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
                'ordering': ('user',),
            },
        ),
    ]