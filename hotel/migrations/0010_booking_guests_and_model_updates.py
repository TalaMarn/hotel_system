# Generated migration for guests field and model metadata updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0009_fix_booking_receipt_and_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='guests',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['roomNo']},
        ),
        migrations.AlterField(
            model_name='room',
            name='isAvailable',
            field=models.BooleanField(
                default=True,
                help_text='Uncheck to hide the room from booking (maintenance, etc.).',
            ),
        ),
    ]
