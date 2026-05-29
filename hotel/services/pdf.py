from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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


def build_booking_slip_pdf(booking):
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
        try:
            logo = Image(str(logo_path), width=1.1 * inch, height=0.75 * inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 8))
        except Exception:
            pass

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
            ['Guests', str(booking.guests)],
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
            ['Nights', str(booking.nights)],
            ['Room Price / Night', f'${booking.room.price}'],
            ['Estimated Total', f'${booking.total_price}'],
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
