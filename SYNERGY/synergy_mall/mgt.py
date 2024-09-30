from synergy_mall.models import Category

product_categories = [
    "Electronics", "Phones & Accessories", "Laptops & Computers",
    "Cameras & Photography", "Headphones & Earbuds",
    "Wearable Technology", "TVs & Audio",
    "Video Games & Accessories", "Smart Home Devices",
    "Home Appliances", "Kitchen Appliances", "Vacuum Cleaners & Floor Care",
    "Furniture", "Bedding & Bath", "Lighting & Lamps", "Home Decor",
    "Carpets & Rugs", "Garden Tools & Supplies",
    "Office Supplies", "Printers & Scanners", "Stationery",
    "Books", "Magazines & Subscriptions", "Music & CDs", "Movies & DVDs",
    "Toys & Games", "Action Figures & Collectibles", "Toys", "Puzzles & Board Games",
    "Baby Products", "Health & Personal Care", "Makeup & Cosmetics", "Fragrances",
    "Men's Grooming", "Fitness Equipment", "Sports & Outdoors", "Camping & Hiking",
    "Cycling", "Fishing & Hunting", "Pet Supplies", "Men's Clothing", "Women's Clothing",
    "Jewelry", "Handbags & Wallets", "Sunglasses & Eyewear", "Watches", "Footwear", "Underwear & Lingerie",
    "Children's Clothing", "School Supplies", "Backpacks & Bags", "Groceries",
    "Snacks & Beverages", "Pantry Staples", "Food", "Organic Products",
    "Wine & Spirits", "Tools & Hardware", "Paint & Wallpaper",
    "Plumbing Supplies", "Electrical Supplies", "Automotive", "Car Electronics",
    "Car Care", "Motorcycle Gear", "Batteries & Chargers",
    "Travel Accessories", "Luggage & Suitcases",
]

sorted_categories = sorted(product_categories)

for category_name in sorted_categories:
    Category.objects.get_or_create(name=category_name)
    print(category_name)
