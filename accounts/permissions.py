from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Assumes the model instance has a `student` attribute or is a `Student` instance.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # If obj is Student itself
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If obj has a student relation
        if hasattr(obj, 'student'):
            return obj.student.user == request.user

        return False
