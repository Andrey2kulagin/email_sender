# Generated by Django 4.2 on 2023-09-02 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0016_alter_senderphonenumber_last_login_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='senderphonenumber',
            name='qr_code',
            field=models.ImageField(default=None, null=True, upload_to=''),
        ),
    ]