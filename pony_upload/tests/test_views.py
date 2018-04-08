from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache


class InitiateUploadViewTest(TestCase):
    def test(self):
        url = reverse('initiate')
        data = {'filename': 'foo.bar'}
        response = self.client.post(url, data=data)
        lease_id = response.content


class UploadPartViewTest(TestCase):
    def setUp(self):
        url = reverse('initiate')
        data = {'filename': 'foo.bar'}
        response = self.client.post(url, data=data)
        self.lease_id = response.content.decode()

    def test(self):
        url = reverse('upload-part')
        headers = {'lease_id': self.lease_id,
                   'part_number': 1}
        content = "FOO"
        response = self.client.put(url, data=content, headers=headers)


class CompleteUploadViewTest(TestCase):
    def setUp(self):
        url = reverse('initiate')
        data = {'filename': 'foo.bar'}
        response = self.client.post(url, data=data)
        self.lease_id = response.content.decode()
        url = reverse('upload-part')
        headers = {'lease_id': self.lease_id, 'part_number': 1}
        content = "FOO"
        response = self.client.put(url, data=content, headers=headers)

    def test(self):
        url = reverse('complete-upload')
        headers = {'lease_id': self.lease_id}
        response = self.client.post(url, headers=headers)


class AbortUploadViewTest(TestCase):
    def setUp(self):
        url = reverse('initiate')
        data = {'filename': 'foo.bar'}
        response = self.client.post(url, data=data)
        self.lease_id = response.content.decode()
        url = reverse('upload-part')
        headers = {'lease_id': self.lease_id, 'part_number': 1}
        content = "FOO"
        response = self.client.put(url, data=content, headers=headers)

    def test(self):
        url = reverse('abort-upload')
        headers = {'lease_id': self.lease_id}
        response = self.client.post(url, headers=headers)


class ListPartsViewTest(TestCase):
    def setUp(self):
        url = reverse('initiate')
        data = {'filename': 'foo.bar'}
        response = self.client.post(url, data=data)
        self.lease_id = response.content.decode()
        url = reverse('upload-part')
        headers = {'lease_id': self.lease_id, 'part_number': 1}
        content = "FOO"
        response = self.client.put(url, data=content, headers=headers)

    def test(self):
        url = reverse('list-parts')
        headers = {'lease_id': self.lease_id}
        response = self.client.get(url, headers=headers)
