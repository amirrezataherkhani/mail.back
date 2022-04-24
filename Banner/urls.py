from django.urls import include, path
from rest_framework.routers import DefaultRouter

from Banner.views import TimeTableViewSet, TimeTables, BannerAPI, AllBanners, CurrentBanner , BannerBuy

router = DefaultRouter()
router.register('timetable', TimeTableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('timetables/', TimeTables.as_view()),

    path('banner/', BannerAPI.as_view()),
    path('banner/<int:pk>/', BannerAPI.as_view()),
    path('banners/', AllBanners.as_view()),
    
    path('banner/<str:banner_id>/buy/', BannerBuy.as_view()),
    path('banner/current/', CurrentBanner.as_view())
]
