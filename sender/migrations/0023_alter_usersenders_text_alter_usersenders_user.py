# Generated by Django 4.2 on 2023-09-07 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0022_admindata_repeat_check_attempt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersenders',
            name='text',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='usersenders',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
