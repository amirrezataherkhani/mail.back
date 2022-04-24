from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Chat.views import ChatAPI, UserChatsAPI, BlockUserInChat, MakeUserAdminInChat, JoinChatAPI, ChangeChatTemporaryLink, \
    ChangeTheChatLink, ChatMessageAPI, ChatMessages, HideMessage, ExitChat, ReportAPI, ChatReports, \
    ReportReasonAPI, AllReportReasonsAPI, SearchMessage

router = DefaultRouter()
router.register('reportreason', ReportReasonAPI)

urlpatterns = [
    path('chat/', ChatAPI.as_view()),
    path('chat/<int:pk>/', ChatAPI.as_view()),
    path('chat/<int:pk>/exit/', ExitChat.as_view()),
    path('chat/mine/', UserChatsAPI.as_view()),
    path('chat/<int:pk>/block/', BlockUserInChat.as_view()),
    path('chat/<int:pk>/admin/', MakeUserAdminInChat.as_view()),
    path('join/<slug>/', JoinChatAPI.as_view()),
    path('chat/<int:pk>/reset/temporary/', ChangeChatTemporaryLink.as_view()),
    path('chat/<int:pk>/reset/slug/', ChangeTheChatLink.as_view()),

    path('message/chat/<int:pk>/', ChatMessageAPI.as_view()),
    path('message/<int:pk>/', ChatMessageAPI.as_view()),
    path('message/<int:pk>/hidden/', HideMessage.as_view()),
    path('message/search/', SearchMessage.as_view()),
    path('chat/<int:pk>/messages/', ChatMessages.as_view()),

    path('', include(router.urls)),
    path('reportreasons/', AllReportReasonsAPI.as_view()),
    path('report/', ReportAPI.as_view()),
    path('reports/', ChatReports.as_view()),
    path('report/<int:pk>/', ReportAPI.as_view()),

]