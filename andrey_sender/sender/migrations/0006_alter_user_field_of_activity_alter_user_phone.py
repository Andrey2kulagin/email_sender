# Generated by Django 4.2 on 2023-04-27 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0005_remove_recipientcontact_contact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='field_of_activity',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Область деятельности'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер телефона'),
        ),
    ]