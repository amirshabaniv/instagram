from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            return obj == request.user
        return True
    

class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)
    

class IsOwner2(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user