# permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow safe methods for anyone (GET)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow owner to update/delete
        return obj.owner == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission: Only the owner of the comment or admin can delete it.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE METHODS (GET, HEAD, OPTIONS) → allow everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow if the user is admin
        if request.user and request.user.is_staff:
            return True

        # Allow if the user is the owner of the comment
        return obj.user == request.user