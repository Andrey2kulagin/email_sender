# Generated by Django 4.2 on 2023-08-27 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0010_contactimportfiles_all_handled_lines_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactimportfiles',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
