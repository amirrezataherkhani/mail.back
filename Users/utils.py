import os

import jwt
from decouple import config
from rest_framework.exceptions import ValidationError

from Users.models import Wallet
from authentication.utils import get_token, get_wallet


def FindWallet(id):
    try:
        p = Wallet.objects.get(id=id)
        return p
    except Wallet.DoesNotExist:
        raise ValidationError('Profile Not Found!')


def VerifyToken(token):
    try:
        decodedToken = jwt.decode(token, config('AUTH_SECRET_KEY'), algorithms=["HS256"])
        return decodedToken
    except Exception as e:
        raise ValidationError('Token is not Valid')


def GiveMeToken(request):
    token = get_token(request)
    DecodedToken = VerifyToken(token)
    return DecodedToken


def GetWallet(request):
    token = get_token(request)
    wallet = get_wallet(token)
    return wallet


