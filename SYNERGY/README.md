## Introduction

Synergy Mall is an e-comerce website that uses wishlists 
to create an avenue for people to gift their loved ones with the exact items they want. 


The site opens with a store with products that can be PURCHASED at once or 
GIFTED to other users who have created WISHLISTS. 


These products are posted there by VENDORS

The website is built on the django framework of python with modules that have been compiled in requirements.txt
After installing the modules in the requirements.txt, the platform can be run using its 'manage.py runserver'


## Features
User registration and authentication
Create and manage wishlists
Add items to wishlists from various e-commerce sites
Share wishlists with friends and family
Place orders for wishlist items
Manage orders and delivery

## Technologies Used
Django
Bootstrap (for front-end styling)
SQLite (default database, can be changed as per need)
Prerequisites
Python 3.6+
Django 3.2+
Virtualenv (recommended)


Installation
### 1. Clone the repository

### 2. Set up a virtual environment
It's recommended to use a virtual environment to manage dependencies. You can set up a virtual environment using venv or virtualenv.

Using venv (Python 3.6+):

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Using virtualenv:

virtualenv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

### 3. Install dependencies
pip install -r requirements.txt

set up .env file to contain the following:
EMAIL_USER='youremail@address.com'
EMAIL_PASS='youremailpassword'
EMAIL_HOST='smtp.ofyouremail.com'

PAY_SECRET='paystack_secret_optional_in_development'


### 4. Set up the database
Apply the migrations to set up the database:

python manage.py makemigrations
python manage.py migrate

### 5. Create new users; both regular users and vendors

### 6. Run the development server
Start the Django development server:

python manage.py runserver
You can now access the application at http://127.0.0.1:8000/.

### Project Structure
```markdown
CnG/
├── .venv/
├── SYNERGY/
│   ├── media/
│   │   ├── identification_images/
│   │   ├── media/
│   │   ├── products/
│   │   └── profile_pictures/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── images/
│   ├── SYNERGY/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── templates/
│       └── base.html
├── synergy_mall/
│   ├── migrations/
│   ├── templates/
│   │   ├── partials/
│   │   └── synergy_mall/
│   ├── 0-views.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── mgt.py
│   ├── models.py
│   ├── payment_functions.py
│   ├── scripts.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── wishlist.py
├── users/
│   ├── migrations/
│   ├── templates/
│   │   ├── coins/
│   │   └── users/
│   ├── 0003_auto_20240908_1534.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── backends.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templatetags/
│   ├── __init__.py
│   └── user_extras.py
├── .env
├── __init__.py
├── db.sqlite3
├── manage.py
├── README.md
├── requirements.txt
└── TODO
```

## Contributing
We welcome contributions to gifter! To contribute:

Fork the repository
Create a new branch (git checkout -b feature/your-feature-name)
Make your changes
Commit your changes (git commit -m 'Add some feature')
Push to the branch (git push origin feature/your-feature-name)
Create a pull request
License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
If you have any questions or suggestions, feel free to contact us at deedadey@gmail.com.

This README provides a clear guide for other developers to understand, set up, and contribute to the de_gifter project. Adjust the links, contact details, and other placeholders as necessary to fit your specific project and needs.

