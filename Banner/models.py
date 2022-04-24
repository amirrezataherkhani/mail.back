from Chat.utils import upload_banner
from Users.models import Wallet
from django.db import models


# Create your models here.

class TimeTable(models.Model):
    DAYS_CHOICES = [
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),

    ]

    day = models.CharField(max_length=1, choices=DAYS_CHOICES)
    start = models.TimeField()
    end = models.TimeField()
    price = models.PositiveIntegerField(blank=True, null=True)


class Banner(models.Model):
    STATUS_CHOICES = [
        ['A', 'Accept'],
        ['W', 'Waiting'],
        ['R', 'Reject']
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    timeTable = models.OneToOneField(TimeTable, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=30)
    link = models.URLField()
    image = models.ImageField(upload_to=upload_banner)
    status = models.CharField(max_length=1, blank=True, default='W', choices=STATUS_CHOICES)
    payed = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.id}'
