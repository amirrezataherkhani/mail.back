from django.contrib import admin

from Users.models import Wallet, FriendRequest

admin.site.register(FriendRequest)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'role']
