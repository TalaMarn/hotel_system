from django.shortcuts import redirect, render

from hotel.models import Room


def customer_dashboard(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('staff_dashboard')

    rooms = Room.objects.filter(isAvailable=True).order_by('id')[:3]
    return render(request, 'pages/home.html', {'rooms': rooms})
