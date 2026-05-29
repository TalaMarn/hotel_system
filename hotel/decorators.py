from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect


def staff_required(view_func):
    @login_required
    @user_passes_test(lambda user: user.is_staff, login_url='customer_dashboard')
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper


def customer_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper
