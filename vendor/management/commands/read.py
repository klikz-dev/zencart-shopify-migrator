from django.core.management.base import BaseCommand
import os
import pymysql.cursors
from pathlib import Path
from tqdm import tqdm

from utils.common import to_int, to_float, to_text, find_file, get_state_from_zip
from utils.feed import read_excel
from vendor.models import Product, Customer, Order

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
        Product.objects.all().delete()

        # Read Database
        with self.connection.cursor() as cursor:
            sql = """
                SELECT
                    p.products_id AS sku,
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
                    pd.products_name AS name,
                    pd.products_description AS description,
                    c.categories_name AS category,
                    m.manufacturers_name AS vendor,
                    pt.type_name AS type
                FROM
                    products p
                LEFT JOIN
                    products_description pd ON p.products_id = pd.products_id
                LEFT JOIN
                    products_to_categories ptc ON p.products_id = ptc.products_id
                LEFT JOIN
                    categories_description c ON ptc.categories_id = c.categories_id
                LEFT JOIN
                    manufacturers m ON p.manufacturers_id = m.manufacturers_id
                LEFT JOIN
                    product_types pt ON p.products_type = pt.type_id;
                """
            cursor.execute(sql)
            feeds = cursor.fetchall()

            for feed in feeds:
                try:
                    type = to_text(feed['type']).replace(
                        "Product - ", "").strip()
                    category = to_text(feed['category']).replace(
                        "<b>", "").replace("</b>", "").strip()
                    free_shipping = to_int(feed['free_shipping']) == 1

                    tags = []
                    if type:
                        tags.append(type)
                    if category:
                        tags.append(category)
                    if free_shipping:
                        tags.append("Free Shipping")
                    tags = ",".join(tags)

                    Product.objects.create(
                        sku=to_int(feed['sku']),
                        name=to_text(feed['name']),
                        description=to_text(feed['description']),

                        vendor="Vins Rare",
                        tags=tags,

                        price=to_float(feed['price']),

                        quantity=to_int(feed['quantity']),
                        weight=to_int(feed['weight']),

                        status=to_int(feed['status']) == 1,
                        track_quantity=to_int(feed['track_quantity']) == 1,

                        thumbnail=f"https://vinsrare.com/images/{
                            to_text(feed['image'])}",

                        min_order_qty=to_int(feed['min_order_qty']),
                        order_increment=to_int(feed['order_increment']),
                    )

                except Exception as e:
                    print(f"{feed['sku']}: {str(e)}")

        # Read Datasheet
        rows = read_excel(
            file_path=f"{FILEDIR}/product-details.xlsx",
            column_map={
                'sku': 'Id',
                'status': 'Status',
                'pre_arrival': 'Pre-Arrival',
                'vintage': 'Vintage',
                'name': 'Name',
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

        for row in rows:
            sku = to_int(row['sku'])

            try:
                product = Product.objects.get(sku=sku)
            except Product.DoesNotExist:
                print(f"{sku} NOT FOUND")
                continue

            product.name = to_text(row['name'])
            product.type = to_text(row['type'])
            product.status = to_text(row['status']) == "On"
            product.roomset = find_file(to_text(row['image_2']), IMAGEDIR)

            product.pre_arrival = to_text(row['pre_arrival'])
            product.vintage = to_text(row['vintage'])
            product.varietal = to_text(row['varietal'])
            product.region = to_text(row['region'])
            product.sub_region = to_text(row['sub_region'])
            product.vineyard = to_text(row['vineyard'])
            product.size = to_text(row['size'])
            product.disgorged = to_text(row['disgorged'])
            product.dosage = to_text(row['dosage'])
            product.alc = to_text(row['alc'])

            product.save()

    def customers(self):
        Customer.objects.all().delete()

        with self.connection.cursor() as cursor:
            sql = """
                SELECT
                    c.customers_firstname AS first_name,
                    c.customers_lastname AS last_name,
                    c.customers_email_address AS email,
                    c.customers_telephone AS phone,
                    c.customers_gender AS gender,
                    c.customers_newsletter AS newsletter,
                    c.customers_newsletter_paper AS sms,
                    a.entry_street_address AS address1,
                    a.entry_suburb as address2,
                    a.entry_company AS company,
                    a.entry_city AS city,
                    a.entry_state AS state,
                    a.entry_postcode AS zip,
                    co.countries_name AS country
                FROM
                    customers c
                LEFT JOIN
                    address_book a ON c.customers_id = a.customers_id
                LEFT JOIN
                    countries co ON a.entry_country_id = co.countries_id;
            """

            cursor.execute(sql)
            customers = cursor.fetchall()

            for customer in customers:
                state = to_text(customer['state'])
                zip = to_text(customer['zip'])
                country = to_text(customer['country'])

                if not state and country == "United States" and zip:
                    state = get_state_from_zip(zip)
                    if str(state) == "nan":
                        state = ""

                try:
                    Customer.objects.create(
                        email=to_text(customer['email']),
                        phone=to_text(customer['phone']),

                        first_name=to_text(customer['first_name']),
                        last_name=to_text(customer['last_name']),
                        company=to_text(customer['company']),
                        address1=to_text(customer['address1']),
                        address2=to_text(customer['address2']),
                        city=to_text(customer['city']),
                        state=state,
                        zip=zip,
                        country=country,

                        newsletter=to_int(customer['newsletter']) == 1,
                        sms=to_int(customer['sms']) == 1,

                        gender="Male" if to_text(
                            customer['gender']) == "m" else "Female",
                    )

                    print(to_text(customer['email']))

                except Exception as e:
                    continue

    def orders(self):
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    SELECT
                        o.orders_id,
                        o.customers_id,
                        o.date_purchased,
                        o.orders_status,
                        ot.text AS order_total,
                        op.products_id,
                        op.products_model,
                        op.products_name,
                        op.final_price,
                        op.products_quantity
                    FROM
                        orders o
                    JOIN
                        orders_products op ON o.orders_id = op.orders_id
                    JOIN
                        orders_total ot ON o.orders_id = ot.orders_id AND ot.class = 'ot_total';
                """
                cursor.execute(sql)
                orders = cursor.fetchall()
                return orders
        except Exception as e:
            print(f"Error fetching orders: {e}")
