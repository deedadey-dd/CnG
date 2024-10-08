# Generated by Django 5.1.1 on 2024-09-08 15:34

from django.db import migrations


def create_categories(apps, schema_editor):
    Category = apps.get_model('synergy_mall', 'Category')
    categories = [
        "Clothing", "Computers", "Phones", "Books", "Home Appliances", "Toys", "Jewelry",
        "Sports Equipment", "Beauty Products", "Furniture", "Automobiles", "Groceries",
        "Outdoor Gear", "Health & Wellness", "Office Supplies", "Pet Supplies", "Kitchenware",
        "Electronics", "Musical Instruments", "Arts & Crafts", "Movies & Music", "Games",
        "Garden Tools", "Baby Products", "Shoes", "Handbags", "Watches", "Accessories",
        "Video Games", "Smartphones", "Laptops", "Tablets", "Camera", "Home Decor",
        "Camping Gear", "Bags & Luggage", "Eyewear", "Fitness Equipment", "Photography",
        "Cycling", "Fishing", "Hiking", "Travel", "Personal Care", "Kitchen Appliances",
        "Furniture & Bedding", "Office Furniture", "Cleaning Supplies", "Party Supplies",
        "Home Improvement", "DIY Tools", "Craft Supplies", "Collectibles", "Specialty Foods"
    ]

    for category in categories:
        Category.objects.get_or_create(name=category)


class Migration(migrations.Migration):

    dependencies = [
        ('synergy_mall', '0002_initial'),
    ]

    operations = [
    ]
