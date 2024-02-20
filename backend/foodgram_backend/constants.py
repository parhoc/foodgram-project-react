import re

INVALID_USERNAMES = (
    'me',
)
EMAIL_MAX_LENGTH = 254
CHAR_FIELD_MAX_LENGTH = 150
HEX_COLOR_REGEX = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
NAME_MAX_LENGTH = 200
HEX_COLOR_LENGTH = 7

# Messages
INVALID_USERNAME_MESSAGE = "Нельзя создать пользователя с логином '{}'"
INGREDIENTS_UNIQUE_ERROR = 'Все ингредиетны должны быть уникальны'
SELF_SUBSCRIPTION_MESSAGE = 'Пользователь не может подписаться сам на себя'
SUBSCRIPTION_DOES_NOT_EXIST = 'Подписка не существует'
REMOVE_ERROR_MESSAGE = 'Рецепта нет в {}'
RECIPE_DOES_NOT_EXIST = 'Рецепт не существует'
COOKING_TIME_ERROR = 'Время приготовления должно быть не меньше 1'
AMOUNT_ERROR = 'Количество должно быть не меньше 1'
