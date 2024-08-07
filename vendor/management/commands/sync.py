from django.core.management.base import BaseCommand

from pathlib import Path

from utils import shopify, common
from vendor.models import Product, Customer, Order

FILEDIR = f"{Path(__file__).resolve().parent.parent}/files"


class Command(BaseCommand):
    help = f"Read Product Datasheet"

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        processor = Processor()

        if "products" in options['functions']:
            processor.products()

        if "collections" in options['functions']:
            processor.collections()

        if "customers" in options['functions']:
            processor.customers()

        if "orders" in options['functions']:
            processor.orders()


class Processor:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def image(self, product):

        images = []
        if product.roomset:
            images.append(product.roomset)

        def sync_image(index, image):
            try:
                shopify_image = shopify.upload_image(
                    shopify_id=product.shopify_id,
                    image=image,
                    alt=product.name,
                    thread=index
                )
                print(
                    f"Uploaded Image {shopify_image.id} for Product {product.shopify_id}")

            except Exception as e:
                print(e)
                return

        for index, image in enumerate(images):
            sync_image(index, image)

    def products(self):

        products = Product.objects.filter(shopify_id=None)
        total = len(products)

        def sync_product(index, product):
            try:
                shopify_product = shopify.create_product(
                    product=product, thread=index)

                if shopify_product.id:
                    product.shopify_id = shopify_product.id
                    product.save()

                    self.image(product)

                    print(
                        f"{index}/{total} -- Product {shopify_product.id} has been created successfully.")

                    shopify.update_inventory(product=product, thread=index)
                else:
                    print(
                        f"Failed uploading - Product {product.product_id}")

            except Exception as e:
                print(e)
                return

        # for index, product in enumerate(products):
        #     sync_product(index, product)

        common.thread(rows=products, function=sync_product)

    def collections(self):
        tags = Product.objects.values_list('tags', flat=True).distinct()
        types = Product.objects.values_list('type', flat=True).distinct()

        collections = []

        for tag in tags:
            for t in tag.split(","):
                if t not in collections:
                    collections.append(t)

        for type in types:
            if type and type not in collections:
                collections.append(type)

        for index, collection in enumerate(collections):
            rules = [{
                'column': "tag",
                'relation': "equals",
                'condition': f"{collection}",
            }]

            shopify_collection = shopify.create_collection(
                title=collection, rules=rules, thread=index)

            print(
                f"Collection {shopify_collection.id} has been setup successfully")

    def customers(self):

        customers = Customer.objects.filter(shopify_id=None)
        total = len(customers)

        def sync_customer(index, customer):

            shopify_customer = shopify.create_customer(
                customer=customer, thread=index)

            if shopify_customer.id:
                customer.shopify_id = shopify_customer.id
                customer.save()
                print(f"{index}/{total} -- Synced customer {shopify_customer.id}")
            else:
                print(f"Error syncing customer {customer.email}")

        # for index, customer in enumerate(customers):
        #     sync_customer(index, customer)

        common.thread(rows=customers, function=sync_customer)

    def orders(self):

        orders = Order.objects.filter(shopify_id=None)
        total = len(orders)

        def sync_order(index, order):

            shopify_order = shopify.create_order(
                order=order, thread=index)

            if shopify_order.id:
                order.shopify_id = shopify_order.id
                order.save()
                print(f"{index}/{total} -- Synced order {shopify_order.id}")
            else:
                print(f"Error syncing order {order.order_id}")

        for index, order in enumerate(orders):
            sync_order(index, order)
            break

        # common.thread(rows=orders, function=sync_order)
