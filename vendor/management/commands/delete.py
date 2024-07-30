from django.core.management.base import BaseCommand

import os
from utils import shopify, common

SHOPIFY_API_BASE_URL = os.getenv('SHOPIFY_API_BASE_URL')
SHOPIFY_API_VERSION = os.getenv('SHOPIFY_API_VERSION')
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_API_THREAD_TOKENS = os.getenv('SHOPIFY_API_THREAD_TOKENS')


class Command(BaseCommand):
    help = f"Delete from Shopify"

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        processor = Processor()

        if "products" in options['functions']:
            processor.products()

        if "customers" in options['functions']:
            processor.customers()


class Processor:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def products(self):
        def delete_product(index, product_id):
            print(f"Deleting {product_id}")
            shopify.delete_product(product_id, thread=index)

        shopify_product_ids = shopify.list_products()

        common.thread(rows=shopify_product_ids, function=delete_product)

    def customers(self):
        def delete_customer(index, customer_id):
            print(f"Deleting {customer_id}")
            shopify.delete_customer(customer_id, thread=index)

        shopify_customer_ids = shopify.list_customers()

        common.thread(rows=shopify_customer_ids, function=delete_customer)
