import datetime

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, GenericAPIView, get_object_or_404
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.generics import ListAPIView, GenericAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from wallet_part.utils import create_part_data , create_part , spend_part_data , spend_from_part

from Banner.models import TimeTable, Banner
from Banner.serializer import TimeTableSerializer, BannerSerializer
from Chat.permission import ReadOnly
from Users.permission import IsAdmin
from Users.utils import GetWallet, GiveMeToken
from rest_framework.response import Response
from decouple import config

# ! Server Information :
SERVICE_ID = config('SERVICE_ID')

class TimeTableViewSet(viewsets.ModelViewSet):
    queryset = TimeTable.objects.all()
    serializer_class = TimeTableSerializer
    # Admin or ReadOnly
    permission_classes = [IsAdmin | ReadOnly]


class TimeTables(ListAPIView):
    queryset = TimeTable.objects.all().order_by('-id')
    serializer_class = TimeTableSerializer
    filterset_fields = ['day', 'start', 'end', 'price']


class BannerAPI(GenericAPIView, CreateModelMixin,
                DestroyModelMixin, RetrieveModelMixin,
                UpdateModelMixin):
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()

    def post(self, request, *args, **kwargs):
        """Create Banner"""
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get Banner"""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Edit Banner"""
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete Banner"""
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(wallet=GetWallet(self.request), status='W')

    def perform_update(self, serializer):
        instance = self.get_object()
        if GiveMeToken(self.request)['role'] == 'admin':
            return serializer.save(wallet=instance.wallet)
        else:
            if instance.wallet == GetWallet(self.request):
                return serializer.save(wallet=instance.wallet, status='W')
            else:
                raise ValidationError('access denied!')

    def perform_destroy(self, instance):
        if GiveMeToken(self.request)['role'] == 'admin' or instance.wallet == GetWallet(self.request):
            return instance.delete()
        else:
            raise ValidationError('access denied!')


class AllBanners(ListAPIView):
    serializer_class = BannerSerializer
    queryset = Banner.objects.filter(payed=True).order_by('-id')
    filterset_fields = ['wallet', 'timeTable', 'title', 'link', 'status']

class BannerBuy(APIView):
    # permission ?
    # permission_classes = []

    def post(self, request, *args, **kwargs):

        # * Take a banner's obj
        target_banner = get_object_or_404(Banner, id=kwargs["banner_id"])
        price = target_banner.timeTable.price

        from authentication.utils import get_token, get_wallet
        # * Get Token & Wallet_id from request:
        token = get_token(request)
        wallet = get_wallet(token)
        
        if target_banner.status == "A":

            # ? create part and spend from part
            data_create_part = create_part_data( wallet_id= wallet, name="create part", amount=price, service_id=SERVICE_ID) 
            part_id = create_part(data_create_part=data_create_part)
            data_spend_from_part = spend_part_data(amount=price)
            response_data = spend_from_part(part_id = part_id , data_spend_from_part = data_spend_from_part)

            # ? Update Banner
            target_banner.payed = True
            
            target_banner.save()

            return Response({"status": True}, status=200)
        
        else:
            raise ValidationError('invalid banner!')
        
class CurrentBanner(GenericAPIView):
    serializer_class = BannerSerializer
    queryset = Banner.objects.filter(payed=True, status='A')

    def get(self, requests, *args, **kwargs):
        now = datetime.datetime.utcnow()
        instance = get_object_or_404(Banner, timeTable__start__lt=now.time(), timeTable__end__gt=now.time()
                                      , timeTable__day=str(now.weekday()+1), payed=True, status='A')
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
