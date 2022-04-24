from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS
from Users import models
from authentication.utils import get_token, get_wallet_and_verify_token, verify_token, verify_token_for_admin, verify_token_for_user


class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        token = get_token(request)
        return verify_token_for_admin(token)


class AdminOrUserReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        token = get_token(request)
        if request.method in SAFE_METHODS:
            return True
        else:
            return verify_token_for_admin(token)


class Admin_And_User(permissions.BasePermission):
    def has_permission(self, request, view):
        token = get_token(request)
        if verify_token_for_admin(token) or verify_token_for_user(token):
            return True
        return False
