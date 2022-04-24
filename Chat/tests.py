import datetime

import jwt
from decouple import config
from rest_framework import status
from rest_framework.test import APITestCase

from Chat.models import Chat, ChatMessage, ReportReason, ReportChat
from Users.models import Wallet


class ChatTest(APITestCase):
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
             'wallet_id': '123e4567-e89b-12d3-a456-426614174000',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.admin = Wallet.objects.create(id='ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
                                           username='admin', role='A')
        self.user = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174000',
                                          username='test')
        self.chat = Chat.objects.create(name='test',
                                        owner=self.admin,
                                        type='C')
        self.chat2 = Chat.objects.create(name='test',
                                         owner=self.admin,
                                         type='C')
        self.chat2.users.add(self.user)

    def test_create_chat(self):
        response = self.client.post('/chat/', HTTP_AUTHORIZATION=self.tokenAdmin,
                                    data={'name': 'test', 'type': 'G'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_edit_chat(self):
        response = self.client.put(f'/chat/1/', HTTP_AUTHORIZATION=self.tokenAdmin,
                                   data={'name': 'test2', 'type': 'C'},
                                   content_type='multipart/form-data; boundary=BoUnDaRyStRiNg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_chat(self):
        response = self.client.get(f'/chat/1/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_chat(self):
        response = self.client.delete(f'/chat/1/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_join_chat(self):
        response = self.client.post(f'/join/{self.chat.slug}/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_exit_chat(self):
        response = self.client.post(f'/chat/{self.chat2.id}/exit/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_chats(self):
        response = self.client.get(f'/chat/mine/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_block_user_in_chat(self):
        response = self.client.post(f'/chat/{self.chat2.id}/block/', data={'user': self.user.id},
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_make_admin_user_in_chat(self):
        response = self.client.post(f'/chat/{self.chat2.id}/admin/', data={'user': self.user.id},
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_temporary_slug_chat(self):
        response = self.client.post(f'/chat/{self.chat2.id}/reset/temporary/',
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_slug_chat(self):
        response = self.client.post(f'/chat/{self.chat2.id}/reset/slug/',
                                    HTTP_AUTHORIZATION=self.tokenAdmin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MessageTest(APITestCase):
    def setUp(self):
        self.tokenUser = jwt.encode(
            {'id': 'facf7b2d-4632-4c13-9ac0-75004a07ca16', 'role': 'admin', 'service': config('SERVICE_ID'),
             'packet_id': 'a5c3f752-bbba-4c4c-ac1f-bbe1b50b0efd', 'username': 'admin',
             'wallet_id': '123e4567-e89b-12d3-a456-426614174000',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.admin = Wallet.objects.create(id='ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
                                           username='admin', role='A')
        self.user = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174000',
                                          username='test')
        self.chat = Chat.objects.create(name='test',
                                        owner=self.admin,
                                        type='G')
        self.chat.users.add(self.user)
        self.chat_message = ChatMessage.objects.create(sender=self.user, chat=self.chat, message='test')

    def test_create_message(self):
        response = self.client.post(f'/message/chat/{self.chat.id}/', HTTP_AUTHORIZATION=self.tokenUser,
                                    data={'message': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_message(self):
        response = self.client.get(f'/message/{self.chat_message.id}/', HTTP_AUTHORIZATION=self.tokenUser, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_message(self):
        response = self.client.delete(f'/message/{self.chat_message.id}/', HTTP_AUTHORIZATION=self.tokenUser, )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_hide_message(self):
        response = self.client.post(f'/message/{self.chat_message.id}/hidden/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_message(self):
        response = self.client.get(f'/message/search/?message={self.chat_message.message}',
                                   HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.json()['results'][0]['message'], self.chat_message.message)

    def test_get_chat_messages(self):
        response = self.client.get(f'/chat/{self.chat.id}/messages/', HTTP_AUTHORIZATION=self.tokenUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestReport(APITestCase):
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
             'wallet_id': '123e4567-e89b-12d3-a456-426614174000',
             'iat': datetime.datetime.now(), 'exp': datetime.datetime.now() + datetime.timedelta(days=1)},
            config('AUTH_SECRET_KEY'),
            algorithm='HS256')
        self.admin = Wallet.objects.create(id='ee8ac4bc-6bd1-4d80-956f-f6589ad9e691',
                                           username='admin', role='A')
        self.user = Wallet.objects.create(id='123e4567-e89b-12d3-a456-426614174000',
                                          username='test')
        self.chat = Chat.objects.create(name='test',
                                        owner=self.admin,
                                        type='G')
        self.chat.users.add(self.user)
        self.chat_message = ChatMessage.objects.create(sender=self.user, chat=self.chat, message='test')
        self.report_reason = ReportReason.objects.create(title='spam')
        self.report_chat = ReportChat.objects.create(reporter=self.user,
                                                     chat=self.chat, reason=self.report_reason)

    def test_create_report(self):
        response = self.client.post('/report/', HTTP_AUTHORIZATION=self.tokenAdmin,
                                    data={'chat': self.chat.id, 'reason': self.report_reason.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_report(self):
        response = self.client.get(f'/report/{self.report_chat.id}/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_report(self):
        response = self.client.delete(f'/report/{self.report_chat.id}/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_report_reason(self):
        response = self.client.post('/reportreason/', HTTP_AUTHORIZATION=self.tokenAdmin,
                                    data={'title': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_report_reason(self):
        response = self.client.get(f'/reportreason/{self.report_reason.id}/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_report_reason(self):
        response = self.client.put(f'/reportreason/{self.report_reason.id}/', HTTP_AUTHORIZATION=self.tokenAdmin,
                                   data={'title': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_report_reason(self):
        response = self.client.delete(f'/reportreason/{self.report_reason.id}/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_report_reasons(self):
        response = self.client.get(f'/reportreasons/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_reports(self):
        response = self.client.get(f'/reports/', HTTP_AUTHORIZATION=self.tokenAdmin, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
