# Generated by Django 4.2 on 2023-09-08 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0027_contactcheckstatistic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactcheckstatistic',
            name='is_check_finished',
        ),
        migrations.AlterField(
            model_name='contactcheckstatistic',
            name='status_data',
            field=models.JSONField(default={'message': 'Процесс начат, но не завершен', 'status_code': 202}),
        ),
    ]
