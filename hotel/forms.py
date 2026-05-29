from django import forms
from .models import Booking, Room, Profile
from django.contrib.auth.models import User
from django.utils import timezone

class LoginForm(forms.Form):
    username = forms.CharField( widget=forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'User Name'

                }))
    password = forms.CharField( widget=forms.PasswordInput(attrs={
                'class':'form-control',
                'placeholder':'Password'

                }))

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    role = forms.ChoiceField(choices=Profile.Role_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Role'
    }), required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'User Name'

            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'Email'

            }
        )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'email', 'check_in', 'check_out', 'special_request', 'receipt']

    customer_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    guests = forms.IntegerField(min_value=1, max_value=5)
    special_request = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Any special requests?'
        })
    )
    receipt = forms.ImageField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        today = timezone.localdate()

        if check_in and check_in < today:
            self.add_error('check_in', 'Check-in date cannot be in the past.')

        if check_in and check_out and check_out <= check_in:
            self.add_error('check_out', 'Check-out date must be after check-in date.')

        return cleaned_data

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['roomNo', 'roomType', 'price', 'roomPic', 'isAvailable']

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['roomNo'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'Room No'

            }
        )
        self.fields['roomType'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'Room Type'

            }
        )
        self.fields['price'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'Price'
            }
        )
        self.fields['roomPic'].widget.attrs.update(
            {
                'class':'form-control',
                'placeholder':'Room Picture'
            }
        )
        self.fields['isAvailable'].widget.attrs.update(
            {
                'class':'form-check-input'
            }
        )
