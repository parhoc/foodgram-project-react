from django.core.exceptions import ValidationError
from foodgram_backend import constants


def validate_username(value):
    if value in constants.INVALID_USERNAMES:
        raise ValidationError(
            f"Username can't be '{value}'",
            params={'value': value}
        )
