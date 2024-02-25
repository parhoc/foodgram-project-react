from rest_framework import serializers


class ImageFieldURL(serializers.ImageField):
    """Custom ImageField with image representation url path."""

    def to_representation(self, value):
        if not value:
            return None
        try:
            return value.url
        except AttributeError:
            return None
