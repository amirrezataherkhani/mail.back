import datetime

from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import SAFE_METHODS

from Users.utils import GetWallet, GiveMeToken


class IsItOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.type == 'P':
            if (obj.owner == GetWallet(request)) or (GetWallet(request) in obj.users.all()):
                return True
            else:
                return False
        else:
            if obj.owner == GetWallet(request):
                return True
            else:
                return False


class IsChatAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if GetWallet(request) in obj.admin.all():
            return True
        else:
            return False


class IsHeBlockedInChat(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        wallet = GetWallet(request)
        if wallet in obj.block.all():
            raise ValidationError('You are not allowed to send message in this chat!')
        else:
            return True


class IsLinkExpired(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        date = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        objDate = obj.temporaryLinkExpiredDate.replace(tzinfo=datetime.timezone.utc)
        delta = objDate - date
        if delta.total_seconds() > 0:
            return True
        else:
            raise ValidationError('LinkExpired')


class IsHeChatUserByMessage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return GetWallet(request) in obj.chat.users.all() or GetWallet(request) == obj.chat.owner


class IsHeChatUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return GetWallet(request) in obj.users.all() or GetWallet(request) == obj.owner


class IsHeBlocked(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if GetWallet(request) in obj.block.all():
            raise ValidationError("You've been blocked!")
        return True


class IsHeBlockedInChatByMessage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if GetWallet(request) in obj.chat.block.all():
            raise ValidationError("You've been blocked!")
        return True


class IsHeSender(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return GetWallet(request) == obj.sender


class IsHeAdminOrOwnerByChat(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if GetWallet(request) in obj.chat.admin.all():
            return True
        elif GetWallet(request) == obj.chat.owner:
            return True
        else:
            return False


class IsChatNotChannel(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.type != 'C':
            return True
        else:
            if obj.owner == GetWallet(request) or GetWallet(request) in obj.admin.all():
                return True
            raise ValidationError("You are not allowed to send message in channel")


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
