from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST


from hotel.forms import BookingForm
from hotel.models import Booking, Room
from hotel.services.availability import get_room_blocked_periods
from hotel.services.pdf import build_booking_slip_pdf


@login_required
def booking_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if not room.isAvailable:
        return render(request, 'pages/unavailable.html', {
            'room': room,
            'reason': 'This room is temporarily unavailable.',
        }, status=403)

    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES, room=room)

        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.room = room
                booking.user = request.user
                booking.save()

            messages.success(request, 'Booking submitted. Download your slip below.')
            return redirect('booking_slip', booking_id=booking.id)
    else:
        form = BookingForm(room=room)

    blocked_periods = list(get_room_blocked_periods(room))

    return render(request, 'pages/booking.html', {
        'form': form,
        'room': room,
        'blocked_periods': blocked_periods,
    })


@login_required
def booking_slip(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    response = HttpResponse(build_booking_slip_pdf(booking), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking-slip-{booking.id}.pdf"'
    return response


@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    return render(request, 'pages/booking_history.html', {'bookings': bookings})


@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.booking_status != 'Pending':
        messages.error(request, 'Only pending bookings can be cancelled.')
        return redirect('history')

    booking.booking_status = 'Cancelled'
    booking.save(update_fields=['booking_status'])
    messages.success(request, f'Booking #{booking.id} has been cancelled.')
    return redirect('history')
