import requests
from rest_framework import exceptions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from Users.models import Wallet

from authentication.permission import Admin_And_User, AdminPermission
from authentication.serializer import *
from authentication.utils import (BASE_AUTH, HOST, ROLE_ID_COADMIN,
                                  ROLE_ID_USER, SERVICE_ID,
                                  check_url_for_create_object, get_role_id,
                                  get_token, get_url_admin_or_user,
                                  get_url_for_address,
                                  get_user_type_by_role_id_for_url, get_wallet,
                                  get_wallet_id, send_request_to_server)


# * Micro Auth
class MicroAuth(APIView):
    def post(self, request, *args, **kwargs):
        wallet_id = request.data['wallet_id']
        if Wallet.objects.filter(id=wallet_id).exists():
            return Response(data={'status': True}, status=200)
        else:
            Wallet.objects.create(id=wallet_id)
            return Response(data={'status': True}, status=200)


# * Auth : Get One User object
class GetUser(APIView):
    permission_classes = [AdminPermission]

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        url = HOST + "/admin/users/" + kwargs["id"]
        return send_request_to_server(url, "get", token=token)


# * Auth : All Users
class AllUser(APIView):
    permission_classes = [AdminPermission]
    serializer_class = FilterSerializer

    def post(self, request, *args, **kwargs):
        token = get_token(request)
        url = HOST + "/admin/users/"
        return send_request_to_server(url=url, request_type="post", token=token)


# * Auth : Register User
class Register(APIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            url = HOST + "/register/"

            response = requests.post(url, json=dict(
                serializer.validated_data), headers={'authbasic': BASE_AUTH})
            if response.status_code == 200:
                js_response = response.json()
            elif response.status_code == 404:
                return Response({'message': response.reason}, status=response.status_code)

            if js_response['status'] != False:
                token = js_response.get('data').get('token')
                role_id = get_role_id(token, service_id=SERVICE_ID)
                wallet_id = get_wallet_id(
                    token, wallet_type_name='Other', service_id=SERVICE_ID, role_id=role_id)

                user_type = get_user_type_by_role_id_for_url(role_id)
                obj_type = check_url_for_create_object(user_type=user_type)

                new_wallet = Wallet.objects.create(
                    id=wallet_id, username=request.data.get('username'), role=obj_type)
                return Response(js_response, status=response.status_code)
            else:
                raise exceptions.ValidationError(
                    detail=js_response, code=response.status_code)


# * Auth : Login User
class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            url = HOST + "/login/"
            return send_request_to_server(url=url, serializer=serializer, request_type="post")

# * Auth: Login Admin


class AdminLogin(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            url = HOST + '/admin/login/'
            return send_request_to_server(url=url, serializer=serializer, request_type="post")


# * Auth : User Info
class MyUserInfo(APIView):

    def post(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_admin_or_user(user_type, "/me")
        return send_request_to_server(url=url, request_type="post", token=token)


# * Auth : Update User Info
class MyInfoUpdate(APIView):
    serializer_class = UpdateSrializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            role_id = get_role_id(token, service_id=SERVICE_ID)
            user_type = get_user_type_by_role_id_for_url(role_id)
            url = get_url_admin_or_user(user_type, "/me/update/")
            return send_request_to_server(url=url, serializer=serializer, request_type="post", token=token)


# * Auth : Logout User
class Logout(APIView):

    def post(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_admin_or_user(user_type, "/logout/")
        return send_request_to_server(url=url, request_type="post", token=token)


# * Auth : Delete User
class DeleteAccount(APIView):
    serializer_class = DeleteSrializer

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            url = HOST + "/delete-my-account"
            token = get_token(request)
            return send_request_to_server(url=url, serializer=serializer, request_type="delete", token=token)


# * Auth : Update Token
class UpdateToken(APIView):
    serializer_class = RefreshTokenSrializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            url = HOST + "/update-token"
            return send_request_to_server(url=url, serializer=serializer, request_type="post")


# * Address : Update + Get + Create
class MyAddress(APIView):
    permission_classes = [Admin_And_User]
    serializer_class = AddressSrializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = get_url_for_address(user_type, main_url="/address")
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_for_address(user_type, main_url="/address")
        return send_request_to_server(url=url, request_type="get", token=token)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            addressId = request.data.get('id', None)
            if user_type == 'user':
                url = HOST + "/address/" + str(addressId)
            elif user_type == "admin":
                url = HOST + "/admin/address/" + str(addressId)
            else:
                raise exceptions.ValidationError(
                    detail="Invalid user type", code=400)
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


# * Address : Get all + one
class AddressSee(GenericAPIView):
    permission_classes = [AdminPermission]
    serializer_class = FilterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/admin/address/"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        addressId = request.data.get('id', None)
        token = get_token(request)
        url = HOST + "/admin/address/" + str(addressId)
        return send_request_to_server(url=url, request_type="get", token=token)


# * Company : Update + Get + Create
class MyCompany(APIView):
    permission_classes = [Admin_And_User]
    serializer_class = CompanySrializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = get_url_for_address(user_type, main_url="/company")
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_for_address(user_type, main_url="/company")
        return send_request_to_server(url=url, request_type="get", token=token)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            companyid = request.data.get('id', None)
            if user_type == 'user':
                url = HOST + "/company/" + str(companyid)
            elif user_type == "admin":
                url = HOST + "/admin/company/" + str(companyid)
            else:
                raise exceptions.ValidationError(
                    detail="Invalid user type", code=400)
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


# * Company : Get all + one
class CompanySee(APIView):
    permission_classes = [AdminPermission]
    serializer_class = FilterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/admin/company/"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        companyid = request.data.get('id', None)
        token = get_token(request)
        url = HOST + "/admin/company/" + str(companyid)
        return send_request_to_server(url=url, request_type="get", token=token)


# * Social Media : Get + Create
class MySocialMedia(APIView):
    permission_classes = [Admin_And_User]
    serializer_class = SocialMediaSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = get_url_for_address(user_type,  main_url="/social-media")
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_for_address(user_type, main_url="/social-media")
        return send_request_to_server(url=url, request_type="get", token=token)


# * Social Media : Get all + one + Update
class SocialMediaSee(APIView):
    permission_classes = [AdminPermission]
    serializer_class = FilterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/admin/social-media/"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        mediaid = request.data.get('id', None)
        token = get_token(request)
        url = HOST + "/admin/social-media/" + str(mediaid)
        return send_request_to_server(url=url, request_type="get", token=token)

    def patch(self, request, *args, **kwargs):
        serializer = SocialMediaSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            mediaid = request.data.get('id', None)
            url = HOST + "/admin/social-media/" + str(mediaid)
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


# * Info : Update + Get + Create
class MyInfo(APIView):
    permission_classes = [Admin_And_User]
    serializer_class = InfoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        if serializer.is_valid(raise_exception=True):
            url = get_url_for_address(user_type, main_url="/info")
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_for_address(user_type, main_url="/info")
        return send_request_to_server(url=url, request_type="get", token=token)


# * Info : Get all + one
class InfoSee(APIView):
    permission_classes = [AdminPermission]
    serializer_class = FilterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/admin/info/"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def get(self, request, *args, **kwargs):
        infoid = request.data.get('id', None)
        token = get_token(request)
        url = HOST + "/admin/info/" + str(infoid)
        return send_request_to_server(url=url, request_type="get", token=token)

    def patch(self, request, *args, **kwargs):
        serializer = InfoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            infoid = request.data.get('id', None)
            url = HOST + "/admin/info/" + str(infoid)
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


# * Session :
class Session(APIView):
    permission_classes = [AdminPermission]

    def post(self, request, *args, **kwargs):
        token = get_token(request)
        sessionId = request.data.get('sessionId', None)
        url = HOST + "/admin/session/"+sessionId
        return send_request_to_server(url=url, request_type="post", data=request.data, token=token)


# * Session :
class SessionSee(APIView):
    permission_classes = [Admin_And_User]

    def post(self, request, *args, **kwargs):
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            role_id = get_role_id(token, service_id=SERVICE_ID)
            user_type = get_user_type_by_role_id_for_url(role_id)
            url = get_url_admin_or_user(user_type, "/session")
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)

    def delete(self, request, *args, **kwargs):
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        user_type = get_user_type_by_role_id_for_url(role_id)
        url = get_url_admin_or_user(
            user_type=user_type, main_url="/session/" + str(request.data.get('id', None)))
        return send_request_to_server(url=url, request_type="delete", token=token)


class SecurityQuestions(APIView):
    permission_classes = [Admin_And_User]

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        url = HOST + "/security-questions"
        return send_request_to_server(url=url, request_type="get", token=token)


class SecurityAnswer(APIView):
    permission_classes = [Admin_And_User]

    def post(self, request, *args, **kwargs):
        serializer = AnsewerSecuritySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/security-answer"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


class RecoveryByLastPassword(APIView):
    permission_classes = [Admin_And_User]

    def post(self, request, *args, **kwargs):
        serializer = Recovery1Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/recovery/by-last-password"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


class RecoveryNewPassword(APIView):
    permission_classes = [Admin_And_User]

    def post(self, request, *args, **kwargs):
        serializer = Recovery2Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = get_token(request)
            url = HOST + "/recovery/new-password"
            return send_request_to_server(url=url, request_type="post", serializer=serializer, token=token)


class ReInfo(APIView):
    permission_classes = [Admin_And_User]

    def patch(self, request, *args, **kwargs):
        token = get_token(request)
        obj = get_wallet(token)
        object_wallet = obj.id
        object_username = obj.username
        object_role = obj.role
        obj.delete()
        Wallet.objects.create(
            id=object_wallet, username=object_username, role=object_role)
        return Response(data={"finish"}, status=200)

class SetCoadminRoleView(APIView):
    permission_classes = [AdminPermission]
    
    def post(self, request):
        url = f'{HOST}/admin/role/{ROLE_ID_COADMIN}/set-role-to-user'
        admin_token = get_token(request)
        serializer = SetOrRemoveCoadminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = send_request_to_server(url=url, request_type='post',serializer=serializer, token=admin_token)
        if response.status_code == status.HTTP_200_OK and response.data.get('status'):
            ...
        return Response(response.data)
    
class RemoveCoadminRoleView(APIView):
    permission_classes = [AdminPermission]
    
    def delete(self, request):
        ...