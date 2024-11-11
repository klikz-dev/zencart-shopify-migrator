# mysql -u root -p --default-character-set=utf8mb4 --force vinsrare < vendor/management/files/source.sql

# python3 manage.py delete orders
# python3 manage.py delete orders
# python3 manage.py delete orders
# python3 manage.py delete customers
# python3 manage.py delete customers
# python3 manage.py delete customers
# python3 manage.py delete products
# python3 manage.py delete products
# python3 manage.py delete products

# python3 manage.py read customers
# python3 manage.py read products
# python3 manage.py read orders

python3 manage.py sync products
python3 manage.py sync products
python3 manage.py sync products
python3 manage.py sync customers
python3 manage.py sync customers
python3 manage.py sync customers
python3 manage.py sync orders
python3 manage.py sync orders
python3 manage.py sync orders

python3 manage.py sync product-status

python3 manage.py export suppliers
python3 manage.py export purchase-orders
python3 manage.py export shipments
