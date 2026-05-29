from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import BookingForm, RegisterForm
from .models import Booking, Profile, Room


class SecurityTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass12345')
        self.other_customer = User.objects.create_user(username='other', password='pass12345')
        self.staff = User.objects.create_user(username='staff', password='pass12345', is_staff=True)
        self.room = Room.objects.create(roomNo='S-101', roomType='Single', price='100.00')
        self.booking = Booking.objects.create(
            user=self.customer,
            room=self.room,
            customer_name='Customer One',
            email='customer@example.com',
            check_in=timezone.localdate() + timedelta(days=1),
            check_out=timezone.localdate() + timedelta(days=2),
        )

    def test_register_form_does_not_expose_staff_role(self):
        form = RegisterForm()
        self.assertNotIn('role', form.fields)

    def test_registration_creates_customer_profile(self):
        response = self.client.post(reverse('register'), {
            'username': 'newcustomer',
            'email': 'new@example.com',
            'password': 'pass12345',
            'confirm_password': 'pass12345',
        })

        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='newcustomer')
        self.assertFalse(user.is_staff)
        self.assertEqual(Profile.objects.get(user=user).role, 'Customer')

    def test_staff_dashboard_requires_staff_user(self):
        self.client.login(username='customer', password='pass12345')
        response = self.client.get(reverse('staff_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(reverse('customer_dashboard')))

    def test_booking_slip_requires_owner_or_staff(self):
        self.client.login(username='other', password='pass12345')
        response = self.client.get(reverse('booking_slip', args=[self.booking.id]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='staff', password='pass12345')
        response = self.client.get(reverse('booking_slip', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)


class BookingFormTests(TestCase):
    def _receipt(self):
        return SimpleUploadedFile(
            'receipt.png',
            b'\x47\x49\x46\x38\x89\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/gif',
        )

    def test_check_in_cannot_be_in_past(self):
        form = BookingForm(
            data={
                'customer_name': 'Customer One',
                'email': 'customer@example.com',
                'check_in': timezone.localdate() - timedelta(days=1),
                'check_out': timezone.localdate() + timedelta(days=1),
                'guests': 1,
            },
            files={'receipt': self._receipt()},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('check_in', form.errors)

    def test_check_out_must_be_after_check_in(self):
        check_in = timezone.localdate() + timedelta(days=1)
        form = BookingForm(
            data={
                'customer_name': 'Customer One',
                'email': 'customer@example.com',
                'check_in': check_in,
                'check_out': check_in,
                'guests': 1,
            },
            files={'receipt': self._receipt()},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('check_out', form.errors)
