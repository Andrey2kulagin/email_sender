# Generated by Django 4.2 on 2023-09-02 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0017_senderphonenumber_qr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='senderphonenumber',
            name='qr_code',
            field=models.ImageField(default=None, null=True, upload_to='C:\\Users\\s121917\\PycharmProjects\\email_sender\\media/qr_codes'),
        ),
    ]
