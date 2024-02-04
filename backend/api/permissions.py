from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """Read only for all users exept administrators and object author."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user == obj.author
                     or request.user.is_staff))
