import datetime

import pytz
from Chat.permission import IsLinkExpired
from Chat.utils import CreateRetrieveDestroyAPIView, RandomString
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (GenericAPIView, ListAPIView,
                                     RetrieveAPIView, UpdateAPIView,
                                     get_object_or_404)
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from Users.models import FriendRequest, Wallet
from Users.permission import (IsAdmin, IsHeBlockedByWallet, IsHeReceiver,
                              IsHeSender)
from Users.serializer import (FriendListSerializer, FriendRequestSerializer,
                              UpdateProfileSerializer, WalletSerializer)
from Users.utils import GetWallet


class ChangeChatTemporaryLink(APIView):
    def post(self, request, *args, **kwargs):
        """Create Temporary Link"""
        user = GetWallet(request)
        user.temporaryLink = RandomString(40)
        user.temporaryLinkExpiredDate = datetime.datetime.now() + \
            datetime.timedelta(hours=1)
        user.temporaryLinkExpiredDate.replace(tzinfo=datetime.timezone.utc)
        user.save()
        data = WalletSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)


class ChangeTheChatLink(APIView):
    def post(self, request, *args, **kwargs):
        """Create Temporary Link"""
        user = GetWallet(request)
        user.slug = RandomString(40)
        user.save()
        data = WalletSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)


class SendFriendRequest(APIView):
    permission_classes = [IsHeBlockedByWallet]

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.get(slug=kwargs['slug'])
            self.check_object_permissions(request=request, obj=wallet)
        except Wallet.DoesNotExist:
            try:
                self.permission_classes = [IsHeBlockedByWallet & IsLinkExpired]
                wallet = Wallet.objects.get(
                    Q(temporaryLink=kwargs['slug']) | Q(slug=kwargs['slug']))
                self.check_object_permissions(request=request, obj=wallet)
            except Wallet.DoesNotExist:
                raise NotFound
        friend_request, created = FriendRequest.objects.get_or_create(sender=GetWallet(request),
                                                                      receiver=wallet)

        if created:
            serializer = FriendRequestSerializer(friend_request)
            data = serializer.data
            status_code = status.HTTP_201_CREATED
        elif friend_request.status == 'W':
            data = {'message': 'friend requeset was already sent'}
            status_code = status.HTTP_204_NO_CONTENT
        elif friend_request.status == 'R':
            serializer = FriendRequestSerializer(
                friend_request, data={'status': 'W'})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data
            status_code = status.HTTP_200_OK
        elif friend_request.status == 'A':
            data = {'message': 'friend request has been accepted'}
            status_code = status.HTTP_204_NO_CONTENT
        return Response(data, status=status_code)


class FriendRequestAPI(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericAPIView):

    serializer_class = FriendRequestSerializer
    queryset = FriendRequest.objects.all()
    permission_classes = [IsHeReceiver]

    def get(self, request, *args, **kwargs):
        """Get Friend Request"""
        self.check_object_permissions(request=request, obj=self.get_object())
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Response To Friend Request A(Accept) or R(Reject)"""
        obj = self.get_object()
        self.check_object_permissions(request=request, obj=obj)
        if obj.status == 'W':
            return self.update(request, *args, **kwargs)
        elif obj.status == 'A' or obj.status == 'R':
            return Response({'message': f'You can\'t change, you {obj.get_status_display()}ed this request before'}, status=status.HTTP_403_FORBIDDEN)

    def perform_update(self, serializer):
        serializer.save()
        if serializer.validated_data.get('status') == 'A':
            sender_username = serializer.data.get('sender').get('username')
            receiver_username = serializer.data.get('receiver').get('username')
            sender = get_object_or_404(
                Wallet, username=sender_username, role='U')
            receiver = get_object_or_404(
                Wallet, username=receiver_username, role='U')
            sender.friends.add(receiver)
            receiver.friends.add(sender)

    def delete(self, request, *args, **kwargs):
        """Delete Friend Request"""
        self.permission_classes = [IsHeSender]
        obj = self.get_object()
        self.check_object_permissions(request=request, obj=obj)
        if obj.status == 'W':
            return self.destroy(request, *args, **kwargs)
        return Response(data={'message': 'You can not delete accepted or rejected request'}, status=status.HTTP_403_FORBIDDEN)


class GetAllFriendRequest(ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        """Get All Friend Requests"""
        qs = GetWallet(
            self.request).friendRequestReceiver.all().order_by('-id')
        return qs


class BlockAPI(APIView):
    def post(self, request, *args, **kwargs):
        """Block"""
        if request.data and 'user' in request.data:
            wallet = GetWallet(request)
            user = get_object_or_404(Wallet, Q(slug=request.data['user']) | Q(
                temporaryLink=request.data['user']))
            if user != wallet:
                if user in wallet.block.all():
                    wallet.block.remove(user)
                else:
                    wallet.block.add(user)
                data = WalletSerializer(wallet).data
                return Response(data, status=status.HTTP_200_OK)
            else:
                raise ValidationError("You can't block yourself!")
        else:
            raise ValidationError('There is no user in the data!')


timezones = [{'id': str(number), 'timezone': pytz.all_timezones[number]} for number in
             range(0, len(pytz.all_timezones))]


class GetAllTimeZonesAPI(APIView):
    def get(self, request, *args, **kwargs):
        return Response(timezones)


class GetMyInfo(RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_object(self):
        return GetWallet(self.request)


class GetInfo(RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_object(self):
        wallet = get_object_or_404(
            Wallet, Q(temporaryLink=self.kwargs['slug']) | Q(slug=self.kwargs['slug']))
        return wallet


class UpdateProfilePicture(UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    queryset = Wallet.objects.all()

    def get_object(self):
        return GetWallet(self.request)


class FriendsListView(APIView):

    def get(self, request):
        user = GetWallet(request)
        serializer = FriendListSerializer(instance=user)
        return Response(serializer.data)


class FriendsDetailView(APIView):

    def get(self, request, friend_id):
        user = GetWallet(request)
        friend = get_object_or_404(Wallet, id=friend_id)
        if friend in user.friends.all():
            serializer = WalletSerializer(instance=friend)
            data = serializer.data
            status_code = status.HTTP_200_OK
        else:
            data = {'message': 'this user is not your friend'}
            status_code = status.HTTP_404_NOT_FOUND
        return Response(data, status=status_code)

    def delete(self, request, friend_id):
        user = GetWallet(request)
        friend = get_object_or_404(Wallet, id=friend_id)
        if friend in user.friends.all():
            user.friends.remove(friend)
            requests_list = FriendRequest.objects.filter(
                Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user))
            requests_list.delete()
            data = {'message': f'{friend.username} removed from your friend'}
            status_code = status.HTTP_200_OK
        else:
            data = {'message': 'this user is not your friend'}
            status_code = status.HTTP_404_NOT_FOUND
        return Response(data, status=status_code)
