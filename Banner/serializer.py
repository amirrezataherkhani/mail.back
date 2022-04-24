from rest_framework import serializers

from Banner.models import TimeTable, Banner
from Users.serializer import WalletSerializer


class TimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True, required=False)

    class Meta:
        model = Banner
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['timeTable'] = TimeTableSerializer(read_only=True)
        return super(BannerSerializer, self).to_representation(instance)

