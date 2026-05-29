from django import forms
from django.utils import timezone

from hotel.models import Booking
from hotel.services.availability import room_has_date_conflict


class BookingForm(forms.ModelForm):
    guests = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={
        'class': 'form-input',
        'min': 1,
        'max': 5,
    }))

    class Meta:
        model = Booking
        fields = [
            'customer_name',
            'email',
            'guests',
            'check_in',
            'check_out',
            'special_request',
            'receipt',
        ]

    def __init__(self, *args, room=None, **kwargs):
        self.room = room
        super().__init__(*args, **kwargs)

        today = timezone.localdate().isoformat()

        self.fields['customer_name'].widget.attrs.update({'class': 'form-input'})
        self.fields['email'].widget.attrs.update({'class': 'form-input'})
        self.fields['check_in'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'min': today,
            'id': 'id_check_in',
        })
        self.fields['check_out'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'min': today,
            'id': 'id_check_out',
        })
        self.fields['special_request'].widget = forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 4,
            'placeholder': 'Any special requests?',
        })
        self.fields['receipt'].widget.attrs.update({'class': 'form-input-file'})

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        today = timezone.localdate()

        if check_in and check_in < today:
            self.add_error('check_in', 'Check-in date cannot be in the past.')

        if check_in and check_out and check_out <= check_in:
            self.add_error('check_out', 'Check-out date must be after check-in date.')

        if self.room and check_in and check_out and not self.errors:
            if not self.room.isAvailable:
                raise forms.ValidationError('This room is currently unavailable for booking.')

            if room_has_date_conflict(self.room, check_in, check_out):
                raise forms.ValidationError(
                    'These dates conflict with an existing reservation for this room.'
                )

        return cleaned_data
