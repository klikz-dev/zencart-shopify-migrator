# Clean up objects - run 3 times each in case of errors.
py manage.py delete orders
py manage.py delete orders
py manage.py delete orders
py manage.py delete customers
py manage.py delete customers
py manage.py delete customers
py manage.py delete products
py manage.py delete products
py manage.py delete products

# Read data
py manage.py read customers
py manage.py read products
py manage.py read orders

# Upload objects - run 3 times each in case of errors.
py manage.py sync products
py manage.py sync products
py manage.py sync products
py manage.py sync customers
py manage.py sync customers
py manage.py sync customers
py manage.py sync orders
py manage.py sync orders
py manage.py sync orders
