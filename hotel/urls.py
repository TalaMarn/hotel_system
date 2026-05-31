from django.urls import path

from hotel import views

urlpatterns = [
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('add-room/', views.add_room, name='add_room'),
    path('rooms/', views.room_list, name='room_list'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('booking/<int:room_id>/', views.booking_view, name='booking'),
    path('booking-slip/<int:booking_id>/', views.booking_slip, name='booking_slip'),
    path('view-receipt/<int:booking_id>/', views.view_receipt, name='view_receipt'),
    path('booking-history/', views.booking_history, name='history'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
]
