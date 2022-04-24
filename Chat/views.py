import datetime

from authentication.utils import (ROLE_ID_COADMIN, SERVICE_ID, get_role_id,
                                  get_token)
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     GenericAPIView, ListAPIView,
                                     RetrieveAPIView, UpdateAPIView,
                                     get_object_or_404)
from rest_framework.response import Response
from rest_framework.views import APIView
from Users.models import Wallet
from Users.permission import IsAdmin
from Users.utils import FindWallet, GetWallet

from Chat.models import Chat, ChatMessage, ReportChat, ReportReason
from Chat.permission import (IsChatAdmin, IsChatNotChannel,
                             IsHeAdminOrOwnerByChat, IsHeBlocked,
                             IsHeBlockedInChat, IsHeBlockedInChatByMessage,
                             IsHeChatUser, IsHeChatUserByMessage, IsHeSender,
                             IsItOwner, IsLinkExpired, ReadOnly)
from Chat.serializer import (ChatMessageSerializer, ChatSerializer,
                             ReportChatSerializer, ReportReasonsSerializer,
                             CreateChatSerializer)
from Chat.utils import (CreateRetrieveDestroyAPIView,
                        CreateUpdateRetrieveDestroyAPIView, RandomString)


class ChatAPI(CreateUpdateRetrieveDestroyAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def put(self, request, *args, **kwargs):
        """Edit Chat"""
        self.permission_classes = [IsItOwner | IsChatAdmin]
        self.check_permissions(request)
        return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get Chat"""
        self.permission_classes = [IsHeChatUser]
        self.check_permissions(request)
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete Chat"""
        self.permission_classes = [IsItOwner | IsAdmin]
        self.check_permissions(request)
        return self.destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = GetWallet(request)
        token = get_token(request)
        role_id = get_role_id(token, service_id=SERVICE_ID)
        serializer = CreateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('type') == 'P':
            contact_user_id = serializer.validated_data.get('users')[0]
            contact_user = get_object_or_404(Wallet, id=contact_user_id.id)
            if contact_user in user.friends.all() or (role_id == ROLE_ID_COADMIN):
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({'message': 'you two are not friends'})
        return super().create(request)

    def perform_create(self, serializer):
        owner = GetWallet(self.request)
        return serializer.save(owner=owner)

    def perform_update(self, serializer):
        chat = self.get_object()
        self.check_object_permissions(self.request, obj=chat)
        return serializer.save(owner=chat.owner, admin=chat.admin.all(), type=chat.type)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, obj=instance)
        return instance.delete()


class UserChatsAPI(ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        """get all users Chat"""
        wallet = GetWallet(self.request)
        userChat = list(wallet.chat.all().order_by('-id'))
        chats = list(Chat.objects.filter(owner=wallet).order_by('-id'))
        return chats + userChat


class BlockUserInChat(APIView):
    permission_classes = [IsItOwner | IsChatAdmin]

    def post(self, request, *args, **kwargs):
        """Block User In Chat"""
        chat = get_object_or_404(Chat, id=kwargs['pk'])
        self.check_object_permissions(self.request, obj=chat)
        if request.data and 'user' in request.data:
            user_wallet_id = request.data['user']
            user = FindWallet(user_wallet_id)
            if user in chat.block.all():
                chat.block.remove(user)
            else:
                chat.block.add(user)

            data = ChatSerializer(chat).data
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No user in data')


class MakeUserAdminInChat(APIView):
    permission_classes = [IsItOwner]

    def post(self, request, *args, **kwargs):
        """Block User In Chat"""
        chat = get_object_or_404(Chat, id=kwargs['pk'])
        self.check_object_permissions(request, obj=chat)
        if request.data and ('user' in request.data):
            user_wallet_id = request.data['user']
            user = FindWallet(user_wallet_id)
            if user in chat.admin.all():
                chat.admin.remove(user)
            else:
                chat.admin.add(user)
            data = ChatSerializer(chat).data
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No user in data')


class ChangeChatTemporaryLink(APIView):
    permission_classes = [IsItOwner | IsChatAdmin]

    def post(self, request, *args, **kwargs):
        """Create Temporary Link"""
        chat = get_object_or_404(Chat, pk=kwargs['pk'])
        self.check_object_permissions(request=request, obj=chat)
        chat.temporaryLink = RandomString(40)
        chat.temporaryLinkExpiredDate = datetime.datetime.now() + \
            datetime.timedelta(hours=1)
        chat.temporaryLinkExpiredDate.replace(tzinfo=datetime.timezone.utc)
        chat.save()
        data = ChatSerializer(chat).data
        return Response(data, status=status.HTTP_200_OK)


class ChangeTheChatLink(APIView):
    permission_classes = [IsItOwner | IsChatAdmin]

    def post(self, request, *args, **kwargs):
        """Create Temporary Link"""
        chat = get_object_or_404(Chat, pk=kwargs['pk'])
        self.check_object_permissions(request=request, obj=chat)
        chat.slug = RandomString(40)
        chat.save()
        data = ChatSerializer(chat).data
        return Response(data, status=status.HTTP_200_OK)


class JoinChatAPI(APIView):
    permission_classes = [IsHeBlockedInChat]

    def post(self, request, *args, **kwargs):
        try:
            chat = Chat.objects.get(slug=kwargs['slug'])
            self.check_object_permissions(request=request, obj=chat)
            chat.users.add(GetWallet(request))
        except Chat.DoesNotExist:
            try:
                self.permission_classes = [IsHeBlockedInChat & IsLinkExpired]
                chat = Chat.objects.get(temporaryLink=kwargs['slug'])
                self.check_object_permissions(request=request, obj=chat)
                chat.users.add(GetWallet(request))
            except Chat.DoesNotExist:
                raise NotFound
        data = ChatSerializer(chat).data
        return Response(data, status=status.HTTP_200_OK)


class ExitChat(APIView):
    permission_classes = [IsHeChatUser]

    def post(self, request, *args, **kwargs):
        chat = get_object_or_404(Chat, id=kwargs['pk'])
        self.check_object_permissions(request, obj=chat)
        user = GetWallet(request)
        if user in chat.users.all():
            chat.users.remove(user)
            data = ChatSerializer(chat).data
            return Response(data, status=status.HTTP_200_OK)
        else:
            raise ValidationError("You can't leave the chat that you own!")


class ChatMessageAPI(CreateRetrieveDestroyAPIView):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = [IsHeBlockedInChatByMessage & IsHeChatUserByMessage]

    def post(self, request, *args, **kwargs):
        """Create Message"""
        self.permission_classes = [
            IsHeChatUser & IsHeBlocked & IsChatNotChannel]
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get Message"""
        self.check_object_permissions(
            request=self.request, obj=self.get_object())
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """delete Message"""
        self.permission_classes = [IsHeSender | IsHeAdminOrOwnerByChat]
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create Message"""
        chat = get_object_or_404(Chat, pk=self.kwargs['pk'])
        self.check_object_permissions(request=self.request, obj=chat)
        return serializer.save(sender=GetWallet(self.request), chat=chat)

    def perform_destroy(self, instance):
        self.check_object_permissions(request=self.request, obj=instance)
        return instance.delete()


class HideMessage(APIView):
    permission_classes = [IsHeChatUserByMessage]

    def post(self, request, *args, **kwargs):
        """Hide message For Me"""
        message = get_object_or_404(ChatMessage, id=kwargs['pk'])
        self.check_object_permissions(request=request, obj=message)
        message.hidden.add(GetWallet(request))
        return Response(ChatMessageSerializer(message).data)


class ChatMessages(ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsHeChatUser & IsHeBlocked]

    def get_queryset(self):
        """Get all Chat's Message"""
        chat = get_object_or_404(Chat, pk=self.kwargs['pk'])
        self.check_object_permissions(request=self.request, obj=chat)
        messages = chat.messages.all().order_by('-id')
        return messages


class ReportReasonAPI(viewsets.ModelViewSet):
    serializer_class = ReportReasonsSerializer
    queryset = ReportReason.objects.all()
    permission_classes = [IsAdmin | ReadOnly]


class AllReportReasonsAPI(ListAPIView):
    """Get All Report Reason"""
    serializer_class = ReportReasonsSerializer
    queryset = ReportReason.objects.all()


class ReportAPI(CreateRetrieveDestroyAPIView):
    serializer_class = ReportChatSerializer
    queryset = ReportChat.objects.all()

    def get(self, request, *args, **kwargs):
        """Get Report"""
        self.permission_classes = [IsAdmin]
        self.check_permissions(request)
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete Report"""
        self.permission_classes = [IsAdmin]
        self.check_permissions(request)
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(reporter=GetWallet(self.request))


class ChatReports(ListAPIView):
    serializer_class = ReportChatSerializer
    permission_classes = [IsAdmin]
    queryset = ReportChat.objects.all().order_by('-id')
    filterset_fields = ['reporter', 'chat']


class SearchMessage(ListAPIView):
    serializer_class = ChatMessageSerializer
    filterset_fields = ['sender__id', 'chat', 'message']

    def get_queryset(self):
        user = GetWallet(self.request)
        messages = ChatMessage.objects.filter(
            Q(chat__in=user.chat.all()) | Q(chat__owner=user)).order_by('-id')
        return messages
