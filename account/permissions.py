from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsDoctor(BasePermission):
    """
    Allows access only to doctors users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.doctors)



