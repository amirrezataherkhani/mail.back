import datetime

import jwt
from decouple import config
from rest_framework import status
from rest_framework.test import APITestCase

from Users.models import Wallet, FriendRequest


class ModelTestcase(APITestCase):
    def setUp(self):
        self.tokenAdmin = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': 'ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.tokenUser = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': '123e4567-e89b-12d3-a456-426614174002',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.tokenUser2 = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': '123e4567-e89b-12d3-a456-426614174080',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.admin = Wallet.objects.create(id='ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
                                           username='admin', role='A')
        self.user = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174002',
                                          username='test1')
        self.user2 = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174080',
                                           username='test2')
        self.user3 = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174020',
                                           username='test3')
        self.friendRequest = FriendRequest.objects.create(sender=self.user,
                                                          receiver=self.user2)

    def test_change_temporary_link(self):
        response = self.client.post('/user/temporarylink/change/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_link(self):
        response = self.client.post('/user/link/change/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_friend_request(self):
        response = self.client.post(f'/user/{self.user3.slug}/friendrequest/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_friend_request(self):
        response = self.client.get(f'/friendrequest/{self.friendRequest.id}/', HTTP_AUTHORIZATION=self.tokenUser2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_friend_request(self):
        response = self.client.put(f'/friendrequest/{self.friendRequest.id}/', HTTP_AUTHORIZATION=self.tokenUser2,
                                   data={'status': 'A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_friend_request(self):
        response = self.client.delete(f'/friendrequest/{self.friendRequest.id}/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_friend_requests(self):
        response = self.client.get(f'/friendrequests/', HTTP_AUTHORIZATION=self.tokenUser2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_block_request(self):
        response = self.client.post(f'/block/', HTTP_AUTHORIZATION=self.tokenUser,
                                    data={'user': self.user2.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
