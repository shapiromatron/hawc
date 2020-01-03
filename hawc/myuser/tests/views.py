from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from myuser import models


class UserCreationTests(TestCase):

    def test_validation_errors(self):
        # assert various errors are present
        view = 'user:new'
        c = Client()
        response = c.post(reverse(view), {
            'email': 'not_email_address',
            'first_name': 'John',
            'last_name': 'Malcovich',
            'password1': 'simple',
            'password2': 'simple',
            'accept_license': ''
        })
        self.assertFormError(
            response, 'form', 'email', 'Enter a valid email address.')
        self.assertFormError(
            response, 'form', 'accept_license',
            'License must be accepted in order to create an account.')
        self.assertFormError(
            response, 'form', 'password1',
            'Password must be at least eight characters in length, at least one special character, and at least one digit.')

    def test_password_match(self):
        # password-match check
        view = 'user:new'
        c = Client()
        response = c.post(reverse(view), {
            'email': 'foo@bar.com',
            'first_name': 'John',
            'last_name': 'Malcovich',
            'password1': 'abcEasy@s123',
            'password2': 'abcEasy@s1234',
            'accept_license': 't'
        })
        self.assertFormError(
            response, 'form', 'password2',
            "Passwords don't match")

    def test_duplicate_email(self):
        # confirm that you can't create two accounts with the same email
        view = 'user:new'
        email = 'duplicate_email@gmail.com'
        form_dict = {
            'email': email,
            'first_name': 'John',
            'last_name': 'Malcovich',
            'password1': 'abcEasy@s123',
            'password2': 'abcEasy@s123',
            'accept_license': 't'
        }

        c = Client()
        response = c.post(reverse(view), form_dict)
        self.assertTrue(models.HAWCUser.objects.filter(email=email).exists())

        c2 = Client()
        response = c2.post(reverse(view), form_dict)
        self.assertFormError(
            response, 'form', 'email',
            "HAWC user with this email already exists.")

    def test_long_email_success(self):
        # confirm you can use a long email address, 200+characters
        view = 'user:new'
        c = Client()
        email = 'a'*200 + '@gmail.com'
        c.post(reverse(view), {
            'email': email,
            'first_name': 'John',
            'last_name': 'Malcovich',
            'password1': 'asdf@asdf1',
            'password2': 'asdf@asdf1',
            'accept_license': 'true'
        })
        self.assertTrue(models.HAWCUser.objects.filter(email=email).exists())
