from django.urls import path

from Users.views import (BlockAPI, ChangeChatTemporaryLink, ChangeTheChatLink,
                         FriendRequestAPI, FriendsListView,
                         GetAllFriendRequest, GetAllTimeZonesAPI, GetInfo,
                         GetMyInfo, SendFriendRequest, UpdateProfilePicture,
                         FriendsDetailView)

urlpatterns = [
    path('friendrequest/', GetAllFriendRequest.as_view()),
    path('friendrequest/<int:pk>/', FriendRequestAPI.as_view()),
    path('friendrequest/user/<slug>/send/', SendFriendRequest.as_view()),
    path('block/', BlockAPI.as_view()),
    path('timezones/', GetAllTimeZonesAPI.as_view()),
    path('me/', GetMyInfo.as_view()),

    path('user/temporarylink/change/', ChangeChatTemporaryLink.as_view()),
    path('user/link/change/', ChangeTheChatLink.as_view()),
    path('user/friends/', FriendsListView.as_view()),
    path('user/friends/<uuid:friend_id>/', FriendsDetailView.as_view()),
    path('user/<slug:slug>/', GetInfo.as_view()),
    path('profilepic/', UpdateProfilePicture.as_view()),

]
