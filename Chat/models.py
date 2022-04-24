from django.db import models
from django.db.models.signals import pre_save, m2m_changed
from rest_framework.exceptions import ValidationError

from Chat.utils import upload_profilepic, upload_file, SlugChecker


class Chat(models.Model):
    TYPE_CHOICES = [
        ['C', 'Channel'],
        ['G', 'Group'],
        ['P', 'Private'],
    ]

    name = models.CharField(max_length=240, blank=True)
    owner = models.ForeignKey('Users.Wallet', on_delete=models.CASCADE, related_name='chat_owner')
    admin = models.ManyToManyField('Users.Wallet', blank=True, related_name='admin_in_chats')
    users = models.ManyToManyField('Users.Wallet', blank=True, related_name="chat")
    profile = models.ImageField(upload_to=upload_profilepic, blank=True)
    block = models.ManyToManyField('Users.Wallet', blank=True, related_name='blocked_in_chats')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='G')
    slug = models.SlugField(max_length=40, blank=True)
    temporaryLink = models.SlugField(max_length=40, blank=True)
    temporaryLinkExpiredDate = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


class ChatMessage(models.Model):
    sender = models.ForeignKey('Users.Wallet', on_delete=models.CASCADE, related_name='messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    file = models.FileField(upload_to=upload_file, blank=True)
    message = models.CharField(max_length=2048)
    hidden = models.ManyToManyField('Users.Wallet', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chat.pk} - {self.pk}'


class ReportReason(models.Model):
    title = models.CharField(max_length=2048)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class ReportChat(models.Model):
    reporter = models.ForeignKey('Users.Wallet', on_delete=models.CASCADE, related_name='report')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='report')
    reason = models.ForeignKey(ReportReason, on_delete=models.CASCADE, related_name='report')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['reporter', 'chat']]

    def __str__(self):
        return str(self.chat.id)


def ChatPreSave(sender, instance, *args, **kwargs):
    if instance.type != 'P':
        if not instance.name:
            raise ValidationError('There is no Name')
    if not instance.slug:
        instance.slug = SlugChecker(Chat)


def ChatUsersM2MChanged(sender, instance, *args, **kwargs):
    if 'post_add' == kwargs['action']:
        if instance.type == 'P':
            if len(instance.users.all()) > 2:
                raise ValidationError('Private Chat must have 2 users!')
            if instance.owner.role == 'U':
                qs1 = instance.users.all()[0].friendRequestReceiver.filter(
                    sender__id=instance.owner.id, status='A')
                qs2 = instance.users.all()[0].friendRequestSender.filter(
                    receiver__id=instance.owner.id, status='A')
                if not qs1.exists() and not qs2.exists():
                    raise ValidationError("You two are not friends!")


def BlockM2MChanged(sender, instance, *args, **kwargs):
    if 'post_add' == kwargs['action']:
        for i in instance.block.all():
            if i.role != 'U':
                raise ValidationError("You can just block normal users")
            instance.users.remove(i)


pre_save.connect(ChatPreSave, Chat)
m2m_changed.connect(ChatUsersM2MChanged, Chat.users.through)
m2m_changed.connect(BlockM2MChanged, Chat.block.through)
