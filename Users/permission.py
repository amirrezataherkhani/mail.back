from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from Users.utils import GetWallet, GiveMeToken


class IsHeBlockedByWallet(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if GetWallet(request) in obj.block.all():
            raise ValidationError("You've been blocked by this user!")
        elif obj in GetWallet(request).block.all():
            raise ValidationError("You've been blocked this user!")
        else:
            return True


class IsHeReceiver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.receiver == GetWallet(request)


class IsHeSender(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == GetWallet(request)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return GiveMeToken(request)['role'] == 'admin'
