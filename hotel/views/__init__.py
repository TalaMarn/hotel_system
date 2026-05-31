from .auth import login_view, logout_view, register_view
from .booking import booking_history, booking_slip, booking_view, cancel_booking
from .customer import customer_dashboard
from .room import add_room, delete_room, edit_room, room_list
from .staff import confirm_booking, staff_dashboard, view_receipt

__all__ = [
    'add_room',
    'booking_history',
    'booking_slip',
    'booking_view',
    'cancel_booking',
    'confirm_booking',
    'customer_dashboard',
    'delete_room',
    'edit_room',
    'login_view',
    'logout_view',
    'register_view',
    'room_list',
    'staff_dashboard',
    'view_receipt',
]
