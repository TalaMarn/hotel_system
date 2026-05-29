from django.contrib.auth.models import User
from django.db import models

from .room import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    ACTIVE_STATUSES = ('Pending', 'Approved')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    guests = models.PositiveSmallIntegerField(default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    special_request = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    receipt = models.ImageField(upload_to='Receipt_Img/', null=True, blank=True)
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer_name} - {self.room.roomNo}'

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def total_price(self):
        return self.room.price * self.nights
