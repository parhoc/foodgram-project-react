from django.core.exceptions import ValidationError

from foodgram_backend import constants


def validate_username(value):
    if value.lower() in constants.INVALID_USERNAMES:
        raise ValidationError(
            constants.INVALID_USERNAME_MESSAGE.format(value),
            params={'value': value}
        )
