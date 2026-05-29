from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from hotel.forms import BookingForm, RegisterForm
from hotel.models import Booking, Profile, Room
from hotel.services.availability import room_has_date_conflict


class SecurityTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass12345')
        self.other_customer = User.objects.create_user(username='other', password='pass12345')
        self.staff = User.objects.create_user(username='staff', password='pass12345', is_staff=True)
        Profile.objects.create(user=self.customer, role='Customer')
        Profile.objects.create(user=self.other_customer, role='Customer')
        Profile.objects.create(user=self.staff, role='Staff')
        self.room = Room.objects.create(roomNo='S-101', roomType='Single', price='100.00')
        self.booking = Booking.objects.create(
            user=self.customer,
            room=self.room,
            customer_name='Customer One',
            email='customer@example.com',
            guests=2,
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

    def test_staff_cannot_create_booking(self):
        self.client.login(username='staff', password='pass12345')
        response = self.client.get(reverse('booking', args=[self.room.id]))

        self.assertRedirects(response, reverse('staff_dashboard'))

    def test_staff_cannot_view_booking_history(self):
        self.client.login(username='staff', password='pass12345')
        response = self.client.get(reverse('history'))

        self.assertRedirects(response, reverse('staff_dashboard'))

    def test_booking_slip_requires_owner_or_staff(self):
        self.client.login(username='other', password='pass12345')
        response = self.client.get(reverse('booking_slip', args=[self.booking.id]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='staff', password='pass12345')
        response = self.client.get(reverse('booking_slip', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)


class BookingFormTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(roomNo='M-202', roomType='Medium', price='150.00')

    def _receipt(self):
        return SimpleUploadedFile(
            'receipt.gif',
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
            room=self.room,
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
            room=self.room,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('check_out', form.errors)


class AvailabilityTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(roomNo='F-303', roomType='Family', price='200.00')
        self.user = User.objects.create_user(username='guest', password='pass12345')
        self.check_in = timezone.localdate() + timedelta(days=5)
        self.check_out = timezone.localdate() + timedelta(days=8)

    def test_overlap_detects_conflicting_booking(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            customer_name='Guest',
            email='guest@example.com',
            guests=3,
            check_in=self.check_in,
            check_out=self.check_out,
            booking_status='Approved',
        )

        self.assertTrue(room_has_date_conflict(self.room, self.check_in, self.check_out))

    def test_rejected_booking_does_not_block_dates(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            customer_name='Guest',
            email='guest@example.com',
            guests=3,
            check_in=self.check_in,
            check_out=self.check_out,
            booking_status='Rejected',
        )

        self.assertFalse(room_has_date_conflict(self.room, self.check_in, self.check_out))
