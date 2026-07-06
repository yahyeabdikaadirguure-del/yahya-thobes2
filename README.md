# Yahya Thobes — Django version

A shop management web app for an Arabic & Islamic clothing store:
inventory with photos, sales recording with automatic stock updates,
and a dashboard with weekly and monthly insights (charts included).

## Run it on your computer

You need Python 3.10 or newer installed (python.org).

```bash
# 1. Open a terminal inside this folder, then create a virtual environment
python -m venv venv

# 2. Activate it
#    Windows:
venv\Scripts\activate
#    Mac / Linux:
source venv/bin/activate

# 3. Install Django and Pillow (for product photos)
pip install -r requirements.txt

# 4. Create the database
python manage.py makemigrations shop
python manage.py migrate

# 5. (Optional) Load the sample thobe & men's wear inventory
python manage.py seed_sample

# 6. Create your admin login
python manage.py createsuperuser

# 7. Start the server
python manage.py runserver
```

Then open http://127.0.0.1:8000 in your browser.
The Django admin panel (for power editing) is at http://127.0.0.1:8000/admin

## Where things live

- `shop/models.py` — Product and Sale database tables
- `shop/views.py` — dashboard, insights, record sale, inventory pages
- `shop/templates/shop/` — the HTML pages
- `media/products/` — uploaded product photos (created automatically)

## Before going live on the internet

1. In `shopmanager/settings.py`: set `DEBUG = False`, put your domain in
   `ALLOWED_HOSTS`, and change `SECRET_KEY` to a long random value.
2. Host on PythonAnywhere (easiest), Railway, or a VPS with gunicorn + nginx.
3. Add Django's login protection so only you and your staff can open it
   (ask Claude to add `@login_required` to the views when you're ready).


## Staff roles (who can do what)

| Role | Sign in as | Dashboard | Record sale | Insights | Add/Edit stock | Delete stock |
|------|-----------|:---------:|:-----------:|:--------:|:--------------:|:------------:|
| Admin | your superuser account | yes | yes | yes | yes | yes |
| Shopkeeper | account in "Shopkeeper" group | yes | yes | yes | yes | no |
| Cashier | account in "Cashier" group | yes | yes | no | no | no |

Set up roles and staff accounts:

```bash
python manage.py setup_roles                                  # create the two groups
python manage.py setup_roles --cashier ali --password 1234    # add a cashier
python manage.py setup_roles --shopkeeper fatima --password 1234  # add a shopkeeper
```

The admin is your `createsuperuser` account. You can also manage everyone
visually in the Django admin at /admin (Users -> pick user -> Groups).

## Thobe & shoe sizing

The size dropdown is grouped:
- General: XS-XXL, Free size
- Kids thobe (height only): 20, 22, 24 ... up to 52
- Men thobe (height-width): 54-20, 54-21 ... 62-28 (42 combinations)
- Shoes: 40 to 46
