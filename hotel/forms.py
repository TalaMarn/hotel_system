from django import forms
from .models import Profile, Booking, Room
from django.contrib.auth.models import User

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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
    
    role = forms.ChoiceField(
        choices=Profile.Role_CHOICES,
        widget=forms.Select(attrs={
            'class':'form-control'
        })
    )
    

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
        fields = ['customer_name', 'email', 'check_in', 'check_out', 'special_request', 'recipt']

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
    recipt = forms.ImageField(required=True)

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
