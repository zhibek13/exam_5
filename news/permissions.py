from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.author == obj.author:
            return True
        else:
            return False


class IsStaffPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_staff:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_staff:
            return True
        else:
            return False
