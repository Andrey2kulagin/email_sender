# Generated by Django 4.2 on 2023-05-04 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0003_alter_recipientcontact_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipientcontact',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipientcontact',
            name='contact_group',
            field=models.ManyToManyField(blank=True, default=[], to='sender.contactgroup'),
        ),
    ]
