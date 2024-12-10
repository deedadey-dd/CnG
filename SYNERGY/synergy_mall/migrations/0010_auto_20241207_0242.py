from django.db import migrations, models
import uuid


def generate_unique_order_numbers(apps, schema_editor):
    Order = apps.get_model('synergy_mall', 'Order')
    orders_to_update = []
    for order in Order.objects.all():
        order.order_number = uuid.uuid4()
        orders_to_update.append(order)
    Order.objects.bulk_update(orders_to_update, ['order_number'])


class Migration(migrations.Migration):
    dependencies = [
        ('synergy_mall', '0009_remove_order_billing_address_and_more'),  # Ensure this is correct
    ]

    operations = [
        migrations.RunPython(generate_unique_order_numbers),
    ]
