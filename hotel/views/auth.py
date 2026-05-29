from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from hotel.forms import LoginForm, RegisterForm
from hotel.models import Profile


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return redirect('customer_dashboard')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )

            if user:
                login(request, user)
                if user.is_staff:
                    return redirect('staff_dashboard')
                return redirect('customer_dashboard')

            messages.error(request, 'Invalid username or password.')

    return render(request, 'pages/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return redirect('customer_dashboard')

    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'An account with that email already exists.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.create(user=user, role='Customer')
                messages.success(request, 'Account created successfully. Please log in.')
                return redirect('login')

    return render(request, 'pages/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
