# Generated by Django 4.2 on 2023-08-02 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0006_import_contactimportfiles'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactimportfiles',
            name='row_len',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
