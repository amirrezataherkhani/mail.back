import os

import pytz
from django.db import models
from django.db.models.signals import m2m_changed, post_save, pre_save

from Chat.models import Chat
from Chat.utils import upload_user_profilepic, SlugChecker
from mail import settings


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_profilePic(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{instance.id}{ext}"
    return f"profiles/{final_name}"


class Wallet(models.Model):
    ROLE_CHOICES = [
        ['U', 'user'],
        ['C', 'co-admin'],
        ['A', 'admin'],
    ]
    id = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=100)
    timezone = models.CharField(max_length=3,
                                choices=[(str(number), pytz.all_timezones[number]) for number in
                                         range(0, len(pytz.all_timezones))],
                                default=str(pytz.all_timezones.index(settings.TIME_ZONE)))
    block = models.ManyToManyField('self', blank=True)
    profilePic = models.ImageField(upload_to=upload_profilePic, blank=True)
    slug = models.SlugField(max_length=40, blank=True)
    temporaryLink = models.SlugField(max_length=40, blank=True)
    temporaryLinkExpiredDate = models.DateTimeField(blank=True, null=True)
    profilePicture = models.FileField(upload_to=upload_user_profilepic, blank=True, null=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=1, default='U')
    friends = models.ManyToManyField('self', blank=True)
    def __str__(self):
        return f'{self.id}'


class FriendRequest(models.Model):
    
    STATUS_CHOICES = [
        ['A', 'Accept'],
        ['W', 'Waiting'],
        ['R', 'Reject']
    ]

    sender = models.ForeignKey(Wallet, related_name="friendRequestSender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Wallet, related_name="friendRequestReceiver", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, blank=True, default='W', choices=STATUS_CHOICES)

    class Meta:
        unique_together = [['sender', 'receiver']]

    def __str__(self):
        return str(self.receiver)
    

def WalletPreSave(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = SlugChecker(Wallet)

def BlockM2MChange(sender, instance, *args, **kwargs):
    if 'post_add' == kwargs['action']:
        for i in instance.block.all():
            friendRequests = FriendRequest.objects.filter(sender__in=[i, instance], receiver__in=[i, instance])
            for friendRequest in friendRequests:
                friendRequest.delete()
            chats = Chat.objects.filter(type='P', owner__in=[i, instance], users__in=[i, instance])
            for chat in chats:
                chat.delete()


def FriendRequestsPostSave(sender, instance, *args, **kwargs):
    if instance.status == 'A':
        chat = Chat(name=f'Private Chat {instance.sender} - {instance.receiver}', owner=instance.sender, type='P')
        chat.save()
        chat.users.add(instance.receiver)


m2m_changed.connect(BlockM2MChange, sender=Wallet.block.through)
pre_save.connect(WalletPreSave, sender=Wallet)
post_save.connect(FriendRequestsPostSave, sender=FriendRequest)
