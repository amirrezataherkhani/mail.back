"""helper fucntions for program related to auth models"""
from Users.models import Wallet
import requests
from rest_framework.response import Response
from rest_framework import status, exceptions
import json
import jwt
from django.core.exceptions import ObjectDoesNotExist
from jwt.exceptions import ExpiredSignatureError
from rest_framework import exceptions
from decouple import config

# ! Server Information :
HOST = config('HOST')
AUTH_SECRET_KEY = config('AUTH_SECRET_KEY')
BASE_AUTH = config('BASE_AUTH')
SERVICE_ID = config('SERVICE_ID')
ROLE_ID_USER = config('ROLE_ID_USER')
ROLE_ID_ADMIN = config('ROLE_ID_ADMIN')
ROLE_ID_COADMIN = config('ROLE_ID_COADMIN')



# todo : Get Wallet
def get_wallet(token):
    role_id = get_role_id(token, service_id=SERVICE_ID)
    try:            
        wallet_id = get_wallet_id(token, wallet_type_name='other', service_id=SERVICE_ID, role_id=role_id)
        wallet_object = Wallet.objects.get(id=wallet_id)
    except ExpiredSignatureError:
        raise exceptions.ValidationError(
            detail={"message":"token Expired"}, code=400)
    except ObjectDoesNotExist:
        raise exceptions.ValidationError(
            detail={"message":"Wallet object not exist"}, code=400)
    except:
        
        print(100*'**', wallet_id)
        raise exceptions.ValidationError(
            detail={"message":"can\'nt return wallet object"}, code=400)
    return wallet_object


# todo : verify token
def verify_token(token):
    try:
        jwt.decode(
            token, AUTH_SECRET_KEY, algorithms=["HS256"])
    except:
        return False

    return True


# todo : verify token for admin
def verify_token_for_admin(token):
    try:
        data = jwt.decode(
            token, AUTH_SECRET_KEY, algorithms=["HS256"])
    except:
        return False
    if data['role'] == 'admin':
        return True
    else:
        return False


# todo : Sent request and return response to client | requests data can set in data or serializer
def send_request_to_server(url, request_type, serializer=None, token=None, data_type=None, data={}):

    if request_type == "post":
        # * for post method without serializer
        if serializer:
            data = serializer.data
        # * Set authbasic for acceptable request & token ( can be None )
        headers = {
            'authbasic': BASE_AUTH,
            'Authorization': f'Bearer {token}' if token else None,
        }
        # ! for request with nested datetime's object can't use data and should use json
        if data_type == "json":
            response = requests.post(url, json=data, headers=headers)
        elif data_type == "files":
            response = requests.post(url, files=data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        else:
            return Response(data={'message': response.reason}, status=response.status_code)

    elif request_type == "delete":
        # * for post method without serializer
        if not serializer == None:
            data = dict(serializer.validated_data)
        # * Set authbasic for acceptable request & token ( can be None )
        headers = {
            'authbasic': BASE_AUTH,
            'Authorization': token,
        }
        response = requests.delete(url, json=data, headers=headers)
        return Response(response.json(), status=response.status_code)

    elif request_type == "get":
        # * Set authbasic for acceptable request & token ( can be None )
        headers = {
            'authbasic': BASE_AUTH,
            'Authorization': token,
        }
        response = requests.get(url, headers=headers)
        return Response(response.json(), status=response.status_code)


# todo : Get token
def get_token(request):
    if 'Authorization' in request.headers:
        return request.headers['Authorization'].split(" ")[-1]
    else:
        raise exceptions.ValidationError(
            detail={"message":"ٌCan\'t found Token"}, code=400)



# todo : Create url ( for Address )
def get_url_for_address(user_type, main_url):
    if user_type == 'user' or user_type == 'coadmin':
        url = HOST + main_url
    elif user_type == "admin":
        url = HOST + "/admin" + main_url 
    else:
        raise exceptions.ValidationError(
            detail={"message":"Invalid user type"}, code=400)
    return url


# todo DRY : Create url for login ( admin or user )
def get_url_admin_or_user(user_type, main_url):
    if user_type == "admin":
        url = HOST + "/admin" + main_url
    elif user_type == "user":
        url = HOST + main_url
    else:
        raise exceptions.ValidationError(detail={"message":"Invalid type"}, code=400)
    return url


def get_wallet_and_verify_token(request):
    token = get_token(request)
    if verify_token(token):
        wallet = get_wallet(token)
        return wallet
    else:
        return False


def is_admin_or_user(request):
    token = get_token(request)
    if verify_token(token):
        return True
    else:
        return False


def verify_token_for_user(token):
    try:
        data = jwt.decode(
            token, AUTH_SECRET_KEY, algorithms=["HS256"])
    except:
        return False
    if data['role'] == 'user':
        return True
    else:
        return False


def check_url_for_create_object(user_type):
    if user_type == 'user':
        return 'U'
    elif user_type == 'coadmin':
        return 'C'


def get_wallet_id(token, wallet_type_name, service_id, role_id):
    try:
        data = jwt.decode(token, AUTH_SECRET_KEY, algorithms=["HS256"])
    except Exception as err:
        raise exceptions.ValidationError(detail={'message':str(err)}, code=400)
    services = data.get('services')
    for service in services:
        if service.get('service_id') == service_id:
            roles = service.get('roles')
            for role in roles:
                if role.get('role_id') == role_id:
                    wallets = role.get('wallets')
                    for wallet in wallets:
                        if wallet.get('wallet_type_name').casefold() == wallet_type_name.casefold():
                            wallet_id = wallet.get('wallet_id')
                            return wallet_id
    return None


def get_role_id(token, service_id):
    try:
        data = jwt.decode(token, AUTH_SECRET_KEY, algorithms=["HS256"])
    except Exception as err:
        raise exceptions.ValidationError(detail={'message':str(err)}, code=400)
        
        
    services = data.get('services')
    for service in services:
        if service.get('service_id') == service_id:
            roles = service.get('roles')
            role_id_list = [role.get('role_id') for role in roles]
            if ROLE_ID_ADMIN in role_id_list:
                return ROLE_ID_ADMIN
            elif ROLE_ID_COADMIN in role_id_list:
                return ROLE_ID_COADMIN
            else:
                return ROLE_ID_USER
            
def get_user_type_by_role_id_for_url(role_id):
    if role_id == ROLE_ID_ADMIN:
        return 'admin'
    elif role_id == ROLE_ID_COADMIN or role_id == ROLE_ID_USER:
        return 'user'
    else:
        return None

# def get_wallet_id_by_user_id(user_id, service_id, role_id, wallet_type_name):
    
#     services = data.get('services')
#     for service in services:
#         if service.get('service_id') == service_id:
#             roles = service.get('roles')
#             for role in roles:
#                 if role.get('role_id') == role_id:
#                     wallets = role.get('wallets')
#                     for wallet in wallets:
#                         if wallet.get('wallet_type_name').casefold() == wallet_type_name.casefold():
#                             wallet_id = wallet.get('wallet_id')
#                             return wallet_id
#     return None