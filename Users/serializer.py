from rest_framework import serializers

from Users.models import Wallet, FriendRequest


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['profilePic']


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = WalletSerializer(read_only=True, required=False)
    receiver = WalletSerializer(read_only=True, required=False)

    class Meta:
        model = FriendRequest
        fields = '__all__'
        

class FriendListSerializer(serializers.ModelSerializer):
    friends = WalletSerializer(read_only=True, many=True)
    class Meta:
        model = Wallet
        fields = ['friends']
