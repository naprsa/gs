from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "user_decks":
            return request.user.is_authenticated
        elif view.action == "deck_detail":
            return True
        elif view.action == "deck_delete":
            return request.user.is_authenticated
        else:
            return False


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action == "deck_update":
            if request.user != obj.user:
                return False

        return True
