# Generated by Django 5.1.1 on 2024-12-01 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('synergy_mall', '0005_wishlistitem_giver_contact_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wishlistitem',
            old_name='message_to_receiver',
            new_name='message',
        ),
    ]
