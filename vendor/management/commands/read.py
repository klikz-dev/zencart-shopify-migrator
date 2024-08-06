from django.core.management.base import BaseCommand
import os
import pymysql.cursors
from pathlib import Path
from tqdm import tqdm

from utils.common import to_int, to_float, to_text, find_file, get_state_from_zip
from utils.feed import read_excel
from vendor.models import Type, Category, Tag, Product, Address, Customer, Order, LineItem

MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

FILEDIR = f"{Path(__file__).resolve().parent.parent}/files"
IMAGEDIR = f"{Path(__file__).resolve().parent.parent}/files/images"


class Command(BaseCommand):
    help = f"Read Datasheet"

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        processor = Processor()

        if "products" in options['functions']:
            processor.products()

        if "customers" in options['functions']:
            processor.customers()

        if "orders" in options['functions']:
            processor.orders()


class Processor:
    def __init__(self):
        self.connection = pymysql.connect(
            host=MYSQL_HOSTNAME,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def products(self):
        Type.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Product.objects.all().delete()

        # Read Database
        with self.connection.cursor() as cursor:
            sql = """
                SELECT
                    p.products_id AS product_id,
                    p.products_price AS price,
                    p.products_image AS image,
                    p.master_categories_id,
                    p.products_qty_box_status AS track_quantity,
                    p.product_is_always_free_shipping AS free_shipping,
                    p.products_quantity_order_min AS min_order_qty,
                    p.products_quantity_order_units AS order_increment,
                    p.products_status AS status,
                    p.products_quantity AS quantity,
                    p.products_weight AS weight,
                    p.products_pre_arrival AS pre_arrival,
                    pd.products_name AS name,
                    pd.products_description AS description,
                    GROUP_CONCAT(c.categories_name) AS categories,
                    pt.type_name AS type,
                    pv.product_vino_location AS warehouse_location,
                    pv.product_vino_year AS year,
                    pv.product_vino_country AS country,
                    pv.product_vino_region AS appellation,
                    pv.product_vino_rating_ws AS ws,
                    pv.product_vino_rating_wa AS wa,
                    pv.product_vino_rating_iwc AS vm,
                    pv.product_vino_rating_cg AS bh,
                    pv.product_vino_rating_view AS jg,
                    pv.product_vino_rating_js AS js,
                    pv.product_vino_rating_other AS additional_notes,
                    pv.product_vino_size AS size,
                    pv.product_vino_wine_searcher AS wine_searcher,
                    pv.product_vino_ct_id AS cellar_tracker_id
                FROM
                    products p
                LEFT JOIN
                    products_description pd ON p.products_id = pd.products_id
                LEFT JOIN
                    products_to_categories ptc ON p.products_id = ptc.products_id
                LEFT JOIN
                    categories_description c ON ptc.categories_id = c.categories_id
                LEFT JOIN
                    product_types pt ON p.products_type = pt.type_id
                LEFT JOIN
                    product_vino_extra pv ON p.products_id = pv.product_vino_id
                GROUP BY
                    p.products_id;
                """
            cursor.execute(sql)
            feeds = cursor.fetchall()

            for feed in tqdm(feeds):
                try:
                    # Type
                    type_name = to_text(feed['type']).replace(
                        "Product - ", "").strip()
                    if type_name:
                        type, _ = Type.objects.get_or_create(name=type_name)

                    # Category
                    categories = []
                    for category_name in to_text(feed['categories']).split(","):
                        category_name = category_name.replace(
                            "<b>", "").replace("</b>", "").strip()
                        if category_name:
                            category, _ = Category.objects.get_or_create(
                                name=category_name)
                            categories.append(category)

                    # Tags
                    tags = []

                    free_shipping = to_int(feed['free_shipping']) == 1
                    if free_shipping:
                        tag, _ = Tag.objects.get_or_create(
                            name="Free Shipping")
                        tags.append(tag)

                    # Name Rebuild
                    name = to_text(feed['name'])
                    year = to_text(feed['year'])
                    if year:
                        name = f"{year} {name}"

                    if not name:
                        continue

                    # Size Rebuild
                    size = to_text(feed['size'])
                    SIZE_MAP = {
                        "p": "375ml",
                        "s": "750ml",
                        "l": "Magnum (1.5l)",
                        "dm": "Double Magnum (3.0l)",
                        "jer": "Jeroboam (4.5l)",
                        "imp": "Imperial (6.0l)",
                        "sal": "Salmanazar (9.0l)",
                        "bal": "Balthazar (12l)"
                    }
                    size = SIZE_MAP.get(size, size)

                    product = Product.objects.create(
                        product_id=to_int(feed['product_id']),
                        name=name,
                        description=to_text(feed['description']),

                        type=type,

                        price=to_float(feed['price']),

                        quantity=to_int(feed['quantity']),
                        weight=to_int(feed['weight']),

                        status=to_int(feed['status']) == 1,
                        track_quantity=to_int(feed['track_quantity']) == 1,

                        thumbnail=f"https://vinsrare.com/images/{
                            to_text(feed['image'])}",

                        min_order_qty=to_int(feed['min_order_qty']),
                        order_increment=to_int(feed['order_increment']),

                        pre_arrival=to_text(feed['pre_arrival']) == "Y",

                        warehouse_location=to_text(feed['warehouse_location']),
                        year=year,
                        country=to_text(feed['country']),
                        appellation=to_text(feed['appellation']),
                        rating_ws=to_text(feed['ws']),
                        rating_wa=to_text(feed['wa']),
                        rating_vm=to_text(feed['vm']),
                        rating_bh=to_text(feed['bh']),
                        rating_jg=to_text(feed['jg']),
                        rating_js=to_text(feed['js']),
                        additional_notes=to_text(feed['additional_notes']),
                        size=size,
                        wine_searcher=to_text(feed['wine_searcher']) == "Y",
                        cellar_tracker_id=to_text(feed['cellar_tracker_id']),
                    )

                    for category in categories:
                        product.categories.add(category)

                    for tag in tags:
                        product.tags.add(tag)

                except Exception as e:
                    print(f"{feed['product_id']}: {str(e)}")

        # Read Datasheet
        rows = read_excel(
            file_path=f"{FILEDIR}/product-details.xlsx",
            column_map={
                'product_id': 'Id',

                'type': 'New "Type"',
                'varietal': 'New: "Varietal"',
                'region': 'New: "Region"',
                'sub_region': 'New "Sub Region"',
                'vineyard': 'New "Vineyard"',
                'size': 'New: "Size"',
                'disgorged': 'New "Disgorged"',
                'dosage': 'New "Dosage"',
                'alc': 'New: "Alc %"',

                'image_2': 'Image #2 Location',
            },
            exclude=[],
            header_id=1,
            get_other_attributes=False
        )

        for row in tqdm(rows):
            product_id = to_int(row['product_id'])

            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                print(f"{product_id} NOT FOUND")
                continue

            # Rewrite Type
            type_name = to_text(row['type'])
            if type_name:
                type, _ = Type.objects.get_or_create(name=type_name)

            # Rewrite Name = vintage + name
            product.type = type
            product.varietal = to_text(row['varietal'])
            product.region = to_text(row['region'])
            product.sub_region = to_text(row['sub_region'])
            product.vineyard = to_text(row['vineyard'])
            product.disgorged = to_text(row['disgorged'])
            product.dosage = to_text(row['dosage'])
            product.alc = to_text(row['alc'])

            product.roomset = find_file(to_text(row['image_2']), IMAGEDIR)

            product.save()

    def customers(self):
        Customer.objects.all().delete()
        Address.objects.all().delete()

        with self.connection.cursor() as cursor:
            sql = """
                SELECT
                    c.customers_id AS customer_id,
                    c.customers_email_address AS email,
                    c.customers_telephone AS phone,
                    c.customers_firstname AS first_name,
                    c.customers_lastname AS last_name,
                    c.customers_gender AS gender,
                    c.customers_newsletter AS newsletter,
                    c.customers_newsletter_paper AS sms,
                    c.customers_default_address_id AS default_address,
                    a.address_book_id AS address_id,
                    a.entry_firstname AS address_first_name,
                    a.entry_lastname AS address_last_name,
                    a.entry_company AS company,
                    a.entry_street_address AS address1,
                    a.entry_suburb AS address2,
                    a.entry_city AS city,
                    a.entry_state AS state,
                    a.entry_postcode AS zip,
                    co.countries_name AS country
                FROM
                    customers c
                LEFT JOIN
                    address_book a ON a.customers_id = c.customers_id
                LEFT JOIN
                    countries co ON a.entry_country_id = co.countries_id;
            """

            cursor.execute(sql)
            customers = cursor.fetchall()

            for customer in tqdm(customers):
                customer_id = to_text(customer['customer_id'])
                address_id = to_int(customer['address_id'])

                state = to_text(customer['state'])
                zip = to_text(customer['zip'])
                country = to_text(customer['country'])

                if not state and country == "United States" and zip:
                    state = get_state_from_zip(zip.split("-")[0])
                    if str(state) == "nan":
                        state = ""

                try:
                    customer_obj, _ = Customer.objects.get_or_create(
                        customer_id=customer_id,
                        defaults={
                            'email': to_text(customer['email']),
                            'phone': to_text(customer['phone']),
                            'first_name': to_text(customer['first_name']),
                            'last_name': to_text(customer['last_name']),
                            'gender': "Male" if to_text(customer['gender']) == "m" else "Female",
                            'newsletter': to_int(customer['newsletter']) == 1,
                            'sms': to_int(customer['sms']) == 1,
                            'default_address': to_int(customer['default_address'])
                        }
                    )

                    Address.objects.create(
                        address_id=address_id,

                        customer=customer_obj,

                        first_name=to_text(customer['address_first_name']),
                        last_name=to_text(customer['address_last_name']),
                        company=to_text(customer['company']),
                        address1=to_text(customer['address1']),
                        address2=to_text(customer['address2']),
                        city=to_text(customer['city']),
                        state=state,
                        zip=zip,
                        country=country,
                    )

                except Exception as e:
                    print(e)
                    continue

    def orders(self):
        Order.objects.all().delete()

        with self.connection.cursor() as cursor:
            sql = """
                    SELECT
                        o.orders_id AS order_id,
                        o.customers_email_address AS email,
                        o.date_purchased AS order_date,
                        os.orders_status_name AS status
                    FROM
                        orders o
                    LEFT JOIN
                        orders_status os ON o.orders_status = os.orders_status_id
                """
            cursor.execute(sql)
            orders = cursor.fetchall()

            for order in orders:
                order_id = order['order_id']

                # Main Order
                try:
                    customer = Customer.objects.get(email=order['email'])
                except Customer.DoesNotExist:
                    print(f"Customer {order['email']} does NOT exist")
                    continue

                try:
                    order_obj = Order.objects.create(
                        customer=customer,
                        order_date=order['order_date'],
                        status=order['status']
                    )
                except Exception as e:
                    print(e)
                    continue

                # Order Prices
                sql = f"""
                    SELECT
                        ot.value,
                        ot.class
                    FROM
                        orders_total ot
                    WHERE
                        ot.orders_id = {order_id}
                """
                cursor.execute(sql)
                prices = cursor.fetchall()

                for price in prices:
                    if price['class'] == "ot_total":
                        order_obj.total_price = to_float(price['value'])
                    if price['class'] == "ot_shipping":
                        order_obj.shipping_price = to_float(price['value'])
                    if price['class'] == "ot_tax":
                        order_obj.tax = to_float(price['value'])

                order_obj.save()

                # Order Line Items
                sql = f"""
                    SELECT
                        op.products_id AS sku,
                        op.final_price as unit_price,
                        op.products_quantity AS quantity
                    FROM
                        orders_products op
                    WHERE
                        op.orders_id = {order_id}
                """
                cursor.execute(sql)
                products = cursor.fetchall()

                for product in products:

                    try:
                        product_obj = Product.objects.get(sku=product['sku'])
                    except Product.DoesNotExist:
                        print(f"Product {product['sku']} does NOT exist.")
                        continue

                    try:
                        LineItem.objects.create(
                            order=order_obj,
                            product=product_obj,
                            unit_price=product['unit_price'],
                            quantity=product['quantity'],
                        )
                    except Exception as e:
                        print(e)
                        continue
