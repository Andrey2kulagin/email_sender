# Generated by Django 4.2 on 2023-07-17 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0006_alter_recipientcontact_whats_reg_checked_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipientcontact',
            name='is_phone_whatsapp_reg',
            field=models.BooleanField(default=False, null=True, verbose_name='Телефон проверен на наличие в WhatsApp'),
        ),
    ]
