from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.contrib.admin.views.decorators import staff_member_required
from hotel.models import Booking
from hotel.services.availability import room_has_date_conflict


@staff_member_required
def staff_dashboard(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')

    bookings = Booking.objects.select_related('room', 'user').order_by('-created_at')

    if status_filter:
        bookings = bookings.filter(booking_status=status_filter)

    if search_query:
        bookings = bookings.filter(
            Q(customer_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(room__roomNo__icontains=search_query)
        )

    customers = User.objects.filter(is_staff=False).order_by('date_joined')

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(booking_status='Pending').count()
    approved_bookings = Booking.objects.filter(booking_status='Approved').count()
    rejected_bookings = Booking.objects.filter(booking_status='Rejected').count()
    cancelled_bookings = Booking.objects.filter(booking_status='Cancelled').count()

    paginator = Paginator(bookings, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'pages/staff_dashboard.html', {
        'bookings': page_obj,
        'customers': customers,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'cancelled_bookings': cancelled_bookings,
        'status_filter': status_filter,
        'search_query': search_query,
    })


@staff_member_required
@require_POST
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    action = request.POST.get('action', 'approve')

    if booking.booking_status != 'Pending':
        messages.error(request, 'This booking has already been processed.')
        return redirect('staff_dashboard')

    if action == 'approve':
        if room_has_date_conflict(
            booking.room,
            booking.check_in,
            booking.check_out,
            exclude_booking_id=booking.id,
        ):
            messages.error(
                request,
                f'Booking #{booking.id} conflicts with another active reservation.',
            )
            return redirect('staff_dashboard')

        booking.booking_status = 'Approved'
        messages.success(request, f'Booking #{booking.id} has been confirmed and approved.')
    elif action == 'reject':
        booking.booking_status = 'Rejected'
        messages.success(request, f'Booking #{booking.id} has been rejected.')

    booking.save(update_fields=['booking_status'])
    return redirect('staff_dashboard')
