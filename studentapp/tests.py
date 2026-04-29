from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import AccountProfile


class AuthenticationFlowTests(TestCase):
    def test_register_student_redirects_to_student_dashboard(self):
        response = self.client.post(reverse('register'), {
            'username': 'student1',
            'first_name': 'Student',
            'last_name': 'User',
            'account_type': AccountProfile.STUDENT,
            'password': 'StrongPassword123',
        })

        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_teacher_login_redirects_to_teacher_dashboard(self):
        user = User.objects.create_user(
            username='teacher1',
            password='StrongPassword123',
            first_name='Teacher',
            last_name='User',
            email='teacher@example.com',
        )
        user.accountprofile.account_type = AccountProfile.TEACHER
        user.accountprofile.save()

        response = self.client.post(reverse('login'), {
            'username': 'teacher1',
            'password': 'StrongPassword123',
        })

        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(response, reverse('teacher_dashboard'))
