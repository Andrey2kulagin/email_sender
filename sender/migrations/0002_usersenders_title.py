# Generated by Django 4.2 on 2023-05-03 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersenders',
            name='title',
            field=models.CharField(blank=True, default='Без названия', max_length=100, null=True),
        ),
    ]
