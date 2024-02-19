from drf_extra_fields.fields import Base64ImageField


class Base64ImageFieldURL(Base64ImageField):
    """Custom Base64ImageField with image representation url path."""

    def to_representation(self, value):
        if not value:
            return None
        try:
            return value.url
        except AttributeError:
            return None
