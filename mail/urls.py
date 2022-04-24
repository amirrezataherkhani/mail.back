"""mail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from mail.utils import update_roles
from mail import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Users.urls')),
    path('', include('Chat.urls')),
    path('', include('Banner.urls')),
    # * Authentication
    path('auth/', include('authentication.urls')),
    # * Wallet
    path('wallet/', include('wallet.urls')),
    path('locked/', include('wallet_locked.urls')),
    path('packet/', include('wallet_packet.urls')),
    path('part/', include('wallet_part.urls')),
    path('payment/', include('wallet_payment.urls')),
    path('transaction/', include('wallet_transaction.urls')),
    path('withdrawal/', include('wallet_withdrawal.urls')),

]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ! update roles (first update admin token)
# update_roles()
