from django.contrib import admin

from Chat.models import Chat, ChatMessage, ReportChat, ReportReason

admin.site.register(Chat)
admin.site.register(ChatMessage)
admin.site.register(ReportChat)
admin.site.register(ReportReason)

