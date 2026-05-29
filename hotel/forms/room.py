from django import forms

from hotel.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['roomNo', 'roomType', 'price', 'roomPic', 'isAvailable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['roomNo'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Room number',
        })
        self.fields['roomType'].widget.attrs.update({'class': 'form-input'})
        self.fields['price'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Price per night',
        })
        self.fields['roomPic'].widget.attrs.update({'class': 'form-input-file'})
        self.fields['isAvailable'].widget.attrs.update({'class': 'form-check-input'})
