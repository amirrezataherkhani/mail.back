import requests
from decouple import config
import pytz

from django.utils import timezone

from Users.utils import GetWallet

BASE_AUTH = config('BASE_AUTH')
HOST = config('HOST')
TOKEN = config('TOKEN')


def update_roles():
    with open("settings.ini", 'r') as reader:
        get_all = reader.readlines()
    response = requests.post(
        url=HOST + "/admin/role", headers={'authbasic': BASE_AUTH, 'Authorization': TOKEN, }
    )
    if response.json()['status'] == True:
        roles = response.json()['data']
        for role in roles:
            if role['name'] == "user":
                ROLE_ID_USER = role['id']
            if role['name'] == "co-admin":
                ROLE_ID_COADMIN = role['id']
        with open('settings.ini', 'w') as reader:
            for i, line in enumerate(get_all, 1):
                if i == 8:
                    reader.writelines("ROLE_ID_USER = " +
                                      ROLE_ID_USER + "\n")
                elif i == 9:
                    reader.writelines("ROLE_ID_COADMIN = " +
                                      ROLE_ID_COADMIN + "\n")
                else:
                    reader.writelines(line)
        print("************Roles Update************")
    else:
        print("************Roles not Update************")


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None
        user = self.get_request_user(request)
        if user:
            tzname = user.timezone
        if tzname:
            timezone.activate(pytz.timezone(pytz.all_timezones[int(tzname)]))
        else:
            timezone.deactivate()
        return self.get_response(request)

    def get_request_user(self, request):
        try:
            return GetWallet(request)
        except:
            return None
