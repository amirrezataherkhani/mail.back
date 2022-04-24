from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from Users.serializer import WalletSerializer
from Users.utils import GetWallet

from Chat.models import Chat, ChatMessage, ReportChat, ReportReason


class CreateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'type', 'name', 'users', 'profile']
        extra_kwargs = {'profile': {'required': False}}


class ChatSerializer(serializers.ModelSerializer):
    owner = WalletSerializer(read_only=True)

    class Meta:
        model = Chat
        extra_kwargs = {'owner': {'required': False},
                        'type': {'required': False},
                        'slug': {'read_only': True},
                        'temporaryLink': {'read_only': True}}
        exclude = []

    def to_representation(self, instance):
        user = GetWallet(self.context.get('request'))
        if instance.type == 'C' and (user in instance.admin.all() or user == instance.owner):
            self.fields['users'] = WalletSerializer(many=True, read_only=True)
            self.fields['admin'] = WalletSerializer(many=True, read_only=True)
            self.fields['block'] = WalletSerializer(many=True, read_only=True)
        else:
            self.Meta.exclude = ['admin', 'block']
        return super(ChatSerializer, self).to_representation(instance)


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = WalletSerializer(required=False, read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'
        extra_kwargs = {'owner': {'required': False},
                        'chat': {'required': False},
                        'hidden': {'read_only': True},
                        'isRead': {'read_only': True}}

    def validate(self, attrs):
        if 'file' in attrs:
            file_size = attrs['file'].size
            limit_mb = 10
            if file_size > limit_mb * 1024 * 1024:
                raise ValidationError(
                    {"file": ["The file must be less than 10MB"]})
        return attrs


class ReportReasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportReason
        fields = '__all__'


class ReportChatSerializer(serializers.ModelSerializer):
    reporter = WalletSerializer(read_only=True, required=False)

    class Meta:
        model = ReportChat
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['chat'] = ChatSerializer(read_only=True)
        return super(ReportChatSerializer, self).to_representation(instance)
