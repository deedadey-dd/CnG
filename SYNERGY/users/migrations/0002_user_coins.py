# Generated by Django 5.1.1 on 2024-10-22 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='coins',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]
