# Generated by Django 4.2 on 2023-08-30 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0012_alter_recipientcontact_is_phone_whatsapp_reg_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersenders',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]
