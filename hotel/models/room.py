from django.db import models


class Room(models.Model):
    ROOM_TYPE = [
        ('Single', 'Single'),
        ('Medium', 'Medium'),
        ('Family', 'Family'),
    ]

    roomNo = models.CharField(max_length=10)
    roomType = models.CharField(max_length=10, choices=ROOM_TYPE, default='Single')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    roomPic = models.ImageField(upload_to='Room_Img/', null=True, blank=True)
    isAvailable = models.BooleanField(
        default=True,
        help_text='Uncheck to hide the room from booking (maintenance, etc.).',
    )

    class Meta:
        ordering = ['roomNo']

    def __str__(self):
        return self.roomNo
