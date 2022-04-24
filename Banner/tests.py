import jwt
from decouple import config
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
import datetime

from Banner.models import TimeTable, Banner
from Users.models import Wallet


class TimeTableAPITestCase(APITestCase):
    def setUp(self):
        self.tokenAdmin = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': 'ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.timetable = TimeTable(day='1', start='11:11', end='11:11', price=100).save()

    def test_create_timetable(self):
        response = self.client.post('/timetable/', data={'day': '1', 'start': '00:00',
                                                         'end': '00:00', 'price': 5000},
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_timetable(self):
        response = self.client.get('/timetable/1/', HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_imetables(self):
        response = self.client.get('/timetables/', HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_timetable(self):
        response = self.client.put('/timetable/1/', data={'day': '1', 'start': '00:00',
                                                          'end': '00:00', 'price': 5000},
                                   HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_timetable(self):
        response = self.client.delete('/timetable/1/', HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BannerAPITestCase(APITestCase):
    def setUp(self):
        self.tokenAdmin = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': '123e4567-e89b-12d3-a456-426614174000',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.wallet_user = Wallet(id='123e4567-e89b-12d3-a456-426614174000', username='test9')
        self.wallet_user.save()
        self.timetable = TimeTable(day='1', start='11:11', end='11:11', price=100)
        self.timetable.save()
        self.timetable2 = TimeTable(day='1', start='11:12', end='11:12', price=100)
        self.timetable2.save()
        self.banner = Banner(wallet=self.wallet_user, title='test',
                             link='https://google.com', image='banner.jpg',
                             timeTable=self.timetable)
        self.banner.save()

    def test_get_banners(self):
        response = self.client.get(f'/banners/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_banner(self):
        response = self.client.get(f'/banner/{self.banner.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_banner(self):
        response = self.client.post(f'/banner/', data={'timeTable': self.timetable2.id, 'title': 'test',
                                                       'link': 'https://google.com/',
                                                       'image': open('static_cdn/media_root/banner/testmodel.jpg',
                                                                     'rb')},
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_edit_banner(self):
        response = self.client.put(f'/banner/{self.banner.id}/', data={'timeTable': self.timetable.id, 'title': 'test',
                                                                       'link': 'https://google.com/',
                                                                       'image': open(
                                                                           'static_cdn/media_root/banner/testmodel.jpg',
                                                                           'rb')},
                                   HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_banner(self):
        response = self.client.delete(f'/banner/{self.banner.id}/',
                                   HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
