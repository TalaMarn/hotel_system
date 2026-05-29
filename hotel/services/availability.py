from hotel.models import Booking


def get_room_blocked_periods(room):
    """Return active reservations (pending or approved) for display on the booking page."""
    return Booking.objects.filter(
        room=room,
        booking_status__in=Booking.ACTIVE_STATUSES,
    ).order_by('check_in').values('check_in', 'check_out', 'booking_status')


def overlapping_bookings(room, check_in, check_out, exclude_booking_id=None):
    queryset = Booking.objects.filter(
        room=room,
        booking_status__in=Booking.ACTIVE_STATUSES,
    ).filter(
        check_in__lt=check_out,
        check_out__gt=check_in,
    )

    if exclude_booking_id:
        queryset = queryset.exclude(id=exclude_booking_id)

    return queryset


def room_has_date_conflict(room, check_in, check_out, exclude_booking_id=None):
    return overlapping_bookings(room, check_in, check_out, exclude_booking_id).exists()


def room_is_bookable(room, check_in=None, check_out=None):
    if not room.isAvailable:
        return False

    if check_in and check_out:
        return not room_has_date_conflict(room, check_in, check_out)

    return True
