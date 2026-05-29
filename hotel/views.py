from io import BytesIO
from pathlib import Path
from django.core.paginator import Paginator
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Profile, Room
from .forms import LoginForm, BookingForm , RegisterForm, RoomForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Create your views here.


staff_required = user_passes_test(lambda user: user.is_staff, login_url='customer_dashboard')

# PDF Generation for Booking Slip
def _build_booking_slip_pdf(booking):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=36,
        bottomMargin=36,
        title=f'Arthy Hotel Booking Slip #{booking.id}',
    )

    styles = getSampleStyleSheet()
    gold = colors.HexColor('#e6b31e')
    charcoal = colors.HexColor('#343434')
    dark = colors.HexColor('#161617')
    cream = colors.HexColor('#fcfaf1')
    muted = colors.HexColor('#c9b980')

    title_style = ParagraphStyle(
        'SlipTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        textColor=gold,
        fontSize=24,
        leading=28,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'SlipSubtitle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        textColor=cream,
        fontSize=11,
        leading=15,
    )
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        textColor=gold,
        fontSize=13,
        leading=16,
        spaceBefore=14,
        spaceAfter=8,
    )
    normal_style = ParagraphStyle(
        'SlipNormal',
        parent=styles['Normal'],
        textColor=dark,
        fontSize=10,
        leading=14,
    )
    note_style = ParagraphStyle(
        'SlipNote',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        textColor=muted,
        fontSize=9,
        leading=13,
    )

    elements = []
    logo_path = Path(settings.BASE_DIR) / 'static' / 'photos' / 'Logo.png'
    if logo_path.exists():
        logo = Image(str(logo_path), width=1.1 * inch, height=0.75 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 8))

    header = Table(
        [[
            Paragraph('Arthy Hotel', title_style),
            Paragraph(
                f'Booking Slip<br/>Receipt No: AH-{booking.id:05d}<br/>Status: {booking.booking_status}',
                subtitle_style,
            ),
        ]],
        colWidths=[230, 260],
    )
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), charcoal),
        ('BOX', (0, 0), (-1, -1), 1.2, gold),
        ('INNERPADDING', (0, 0), (-1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph('Customer Details', section_style))
    customer_table = Table(
        [
            ['Customer Name', booking.customer_name],
            ['Email', booking.email],
            ['Created At', booking.created_at.strftime('%Y-%m-%d %H:%M')],
        ],
        colWidths=[150, 340],
    )
    customer_table.setStyle(_booking_table_style(gold, charcoal, cream))
    elements.append(customer_table)

    elements.append(Paragraph('Stay Details', section_style))
    stay_table = Table(
        [
            ['Room Number', booking.room.roomNo],
            ['Room Type', booking.room.roomType],
            ['Check-in Date', booking.check_in],
            ['Check-out Date', booking.check_out],
            ['Room Price', f'${booking.room.price}'],
        ],
        colWidths=[150, 340],
    )
    stay_table.setStyle(_booking_table_style(gold, charcoal, cream))
    elements.append(stay_table)

    elements.append(Paragraph('Special Request', section_style))
    request_text = booking.special_request or 'No special request provided.'
    request_table = Table(
        [[Paragraph(str(request_text), normal_style)]],
        colWidths=[490],
    )
    request_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#d8c47a')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9df')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(request_table)
    elements.append(Spacer(1, 24))

    footer = Table(
        [[Paragraph('Thank you for choosing Arthy Hotel. Please keep this slip for check-in confirmation.', note_style)]],
        colWidths=[490],
    )
    footer.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), charcoal),
        ('BOX', (0, 0), (-1, -1), 1, gold),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(footer)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def _booking_table_style(gold, charcoal, cream):
    return TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#d8c47a')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8ddb2')),
        ('BACKGROUND', (0, 0), (0, -1), charcoal),
        ('TEXTCOLOR', (0, 0), (0, -1), gold),
        ('BACKGROUND', (1, 0), (1, -1), cream),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#161617')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])



def customer_dashboard(request):
    rooms = Room.objects.all().order_by('id')[:3]
    context = {
        'rooms': rooms,
    }

    return render(request, 'customer_dashboard.html', context)

@login_required
@staff_required
def staff_dashboard(request):
    rooms = Room.objects.all().order_by('id')[:3]
    context = {
        'rooms': rooms,
    }

    return render(request, 'staff_dashboard.html', context)

def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user:
                login(request, user)
                if user.is_staff:
                    return redirect('staff_dashboard')
                return redirect('customer_dashboard')
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': form})

def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'An account with that email already exists.')
            elif password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.create(user=user, role='Customer')
                messages.success(request, 'Account created successfully. Please log in.')
                return redirect('login')

    return render(request, 'register.html', {'form': form})



@login_required
def roomList(request):
    query = request.GET.get('q', '')
    available_only = request.GET.get('available') == '1'
    if query:
        rooms = Room.objects.filter(roomNo__icontains=query).order_by('id')
    else:
        rooms = Room.objects.all().order_by('id')

    if available_only:
        rooms = rooms.filter(isAvailable=True)

    paginator = Paginator(rooms, 9)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    page_numbers = range(
        max(page_obj.number - 1, 1),
        min(page_obj.number + 1, paginator.num_pages) + 1
    )
    return render(request, 'room_list.html', {
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'query': query,
        'available_only': available_only,
    })

@login_required(login_url='login')
@staff_required
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form, 'is_edit': False})

@login_required(login_url='login')
@staff_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = RoomForm(instance=room)
    return render(request, 'add_room.html', {'form': form, 'room': room, 'is_edit': True})

@login_required(login_url='login')
@staff_required
@require_POST
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('room_list')

@login_required
def booking_view(request, room_id):

    user = get_object_or_404(User, id=request.user.id)
    room = get_object_or_404(Room, id=room_id)

    # Prevent booking unavailable room
    if not room.isAvailable:
        return render(request, '404.html')

    if request.method == 'POST':

        form = BookingForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                locked_room = Room.objects.select_for_update().get(id=room.id)

                if not locked_room.isAvailable:
                    return render(request, '404.html')

                booking = form.save(commit=False)
                booking.room = locked_room
                booking.user = user
                booking.save()

                locked_room.isAvailable = False
                locked_room.save(update_fields=['isAvailable'])

            return redirect('booking_slip', booking_id=booking.id)

    else:
        form = BookingForm()

    return render(request, 'booking_page.html', {
        'form': form,
        'room': room
    })

@login_required
def booking_slip(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    response = HttpResponse(_build_booking_slip_pdf(booking), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking-slip-{booking.id}.pdf"'
    return response

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'booking_history.html', {'bookings': bookings})

def logout_view(request):
    logout(request)
    return redirect('login')
