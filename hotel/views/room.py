from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST


from hotel.forms import RoomForm
from hotel.models import Room
from hotel.services.availability import overlapping_bookings


@login_required
def room_list(request):
    query = request.GET.get('q', '')
    available_only = request.GET.get('available') == '1'
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')

    rooms = Room.objects.all()

    if query:
        rooms = rooms.filter(
            Q(roomNo__icontains=query) | Q(roomType__icontains=query)
        )

    if available_only:
        rooms = rooms.filter(isAvailable=True)

    rooms = rooms.order_by('roomNo')

    paginator = Paginator(rooms, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_numbers = range(
        max(page_obj.number - 1, 1),
        min(page_obj.number + 1, paginator.num_pages) + 1,
    )

    room_cards = []
    for room in page_obj:
        conflict = False
        if check_in and check_out:
            try:
                from datetime import datetime
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                conflict = overlapping_bookings(room, check_in_date, check_out_date).exists()
            except ValueError:
                check_in = ''
                check_out = ''

        room_cards.append({
            'room': room,
            'has_conflict': conflict,
            'can_book': room.isAvailable and not conflict,
        })

    return render(request, 'pages/room_list.html', {
        'page_obj': page_obj,
        'room_cards': room_cards,
        'page_numbers': page_numbers,
        'query': query,
        'available_only': available_only,
        'check_in': check_in,
        'check_out': check_out,
    })


@staff_member_required
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = RoomForm()

    return render(request, 'pages/room_form.html', {'form': form, 'is_edit': False})


@staff_member_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = RoomForm(instance=room)

    return render(request, 'pages/room_form.html', {
        'form': form,
        'room': room,
        'is_edit': True,
    })


@staff_member_required
@require_POST
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('staff_dashboard')
