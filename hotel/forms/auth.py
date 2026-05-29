from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Username',
        'autocomplete': 'username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password',
        'autocomplete': 'current-password',
    }))


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password',
        'autocomplete': 'new-password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Confirm password',
        'autocomplete': 'new-password',
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Email address',
            'autocomplete': 'email',
        })

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data
