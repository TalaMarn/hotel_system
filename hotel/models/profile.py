from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    Role_CHOICES = [
        ('Customer', 'Customer'),
        ('Staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role_CHOICES, default='Customer')

    def __str__(self):
        return self.user.username

    def sync_role_from_user(self):
        role = 'Staff' if self.user.is_staff else 'Customer'
        if self.role != role:
            self.role = role
            self.save(update_fields=['role'])
