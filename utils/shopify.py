import os
import base64
import json
import requests
from pathlib import Path
from datetime import datetime
import shopify
from utils import common

SHOPIFY_API_BASE_URL = os.getenv('SHOPIFY_API_BASE_URL')
SHOPIFY_API_VERSION = os.getenv('SHOPIFY_API_VERSION')
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_API_THREAD_TOKENS = os.getenv('SHOPIFY_API_THREAD_TOKENS')

FILEDIR = f"{Path(__file__).resolve().parent.parent}/vendor/management/files"


class Processor:
    def __init__(self, thread=None):

        self.api_token = SHOPIFY_API_TOKEN

        if thread != None:
            self.api_token = SHOPIFY_API_THREAD_TOKENS.split(",")[thread % 5]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def generate_product_metafields(self, product):
        metafield_keys = [
            'min_order_qty',
            'order_increment',

            'pre_arrival',

            'warehouse_location',
            'year',
            'country',
            'appellation',
            'rating_ws',
            'rating_wa',
            'rating_vm',
            'rating_bh',
            'rating_jg',
            'rating_js',
            'additional_notes',
            'size',
            'wine_searcher',
            'cellar_tracker_id',

            'varietal',
            'region',
            'sub_region',
            'vineyard',
            'disgorged',
            'dosage',
            'alc',
        ]

        metafields = []
        for metafield_key in metafield_keys:
            metafield_value = getattr(product, metafield_key)

            metafield = {
                "namespace": "custom",
                "key": metafield_key,
                "value": metafield_value
            }

            metafields.append(metafield)

        return metafields

    def generate_product_data(self, product):

        # Tags
        tags = []

        categories = product.categories.all()
        for category in categories:
            tags.append(f"{category.name}")

        for tag in product.tags.all():
            tags.append(f"{tag.name}")

        tags = ",".join(tags)

        # Type
        type = ""
        if product.type:
            type = product.type.name

        product_data = {
            "title": product.name.title(),
            "body_html": product.description,
            "vendor": "Vins Rare",
            "product_type": type,
            "tags": tags,
        }

        if not product.status:
            product_data['published_at'] = None
            product_data['published_scope'] = 'web'

        return product_data

    def generate_variant_data(self, product, option=None):

        variant_data = {
            'price': product.price,
            'sku': f"VR-{product.product_id}",
            'weight': product.weight,
            'weight_unit': 'lb',
            'inventory_management': "shopify" if product.track_quantity else None,
            'fulfillment_service': 'manual',
            'inventory_quantity': product.quantity,
            'taxable': False,
        }

        if option:
            variant_data['option1'] = option

        return variant_data

    def generate_customer_metafields(self, customer):
        metafield_keys = [
            'gender',
        ]

        metafields = []
        for metafield_key in metafield_keys:
            metafield_value = getattr(customer, metafield_key)

            metafield = {
                "namespace": "custom",
                "key": metafield_key,
                "value": metafield_value
            }

            metafields.append(metafield)

        return metafields


def list_products(thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        all_shopify_product_ids = []
        shopify_products = shopify.Product.find(limit=250)

        while shopify_products:

            print(f"Fetched {len(shopify_products)} Products")

            for shopify_product in shopify_products:
                all_shopify_product_ids.append(shopify_product.id)

            shopify_products = shopify_products.has_next_page(
            ) and shopify_products.next_page() or []

        return all_shopify_product_ids


def create_product(product, thread=None):

    processor = Processor(thread=thread)

    product_data = processor.generate_product_data(product=product)
    variant_data = processor.generate_variant_data(product=product)
    metafields = processor.generate_product_metafields(product=product)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_product = shopify.Product()
        for key in product_data.keys():
            setattr(shopify_product, key, product_data.get(key))

        shopify_variant = shopify.Variant()
        for key in variant_data.keys():
            setattr(shopify_variant, key, variant_data.get(key))
        shopify_product.variants = [shopify_variant]

        if shopify_product.save():

            for metafield in metafields:
                shopify_metafield = shopify.Metafield()
                shopify_metafield.namespace = metafield['namespace']
                shopify_metafield.key = metafield['key']
                shopify_metafield.value = metafield['value']
                shopify_product.add_metafield(shopify_metafield)

            if product.thumbnail:
                shopify_image = shopify.Image()
                shopify_image.src = product.thumbnail
                shopify_image.position = 1
                shopify_product.images = [shopify_image]
                shopify_product.save()

        else:
            print(shopify_product.errors.full_messages())

        return shopify_product


def delete_product(id, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_product = shopify.Product.find(id)
        success = shopify_product.destroy()

        return success


def upload_image(shopify_id, image, alt, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        with open(image, "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')

            image_obj = {
                'product_id': shopify_id,
                'attachment': encoded_string,
                'filename': os.path.basename(image),
                'alt': alt,
                'position': 2,
            }

            shopify_image = shopify.Image(image_obj)
            shopify_image.save()

            return shopify_image


def update_inventory(product, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_product = shopify.Product.find(product.shopify_id)
        for shopify_variant in shopify_product.variants:
            inventory_item_id = shopify_variant.inventory_item_id

            inventory_levels = shopify.InventoryLevel.find(
                inventory_item_ids=inventory_item_id, location_ids='76827230447')

            if inventory_levels:
                inventory_level = inventory_levels[0]
                inventory_level.set(location_id='76827230447',
                                    inventory_item_id=inventory_item_id, available=product.quantity)

                print(
                    f"Product {product.shopify_id} Inventory updated to {product.quantity}")

            else:
                print(
                    f"Failed updating inventory for product {product.shopify_id}")

        return


def create_collection(title, rules, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_collection = shopify.SmartCollection()

        shopify_collection.title = title
        shopify_collection.rules = rules
        shopify_collection.save()

        return shopify_collection


def list_customers(thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        all_shopify_customer_ids = []
        shopify_customers = shopify.Customer.find(limit=250)

        while shopify_customers:

            print(f"Fetched {len(shopify_customers)} Customers")

            for shopify_customer in shopify_customers:
                all_shopify_customer_ids.append(shopify_customer.id)

            shopify_customers = shopify_customers.has_next_page(
            ) and shopify_customers.next_page() or []

        return all_shopify_customer_ids


def create_customer(customer, thread=None):
    processor = Processor(thread=thread)

    metafields = processor.generate_customer_metafields(customer=customer)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        customer_data = {
            "email": customer.email,
            "phone": customer.phone,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "addresses": [
                {
                    "company": customer.company,
                    "address1": customer.address1,
                    "address2": customer.address2,
                    "city": customer.city,
                    "province": customer.state,
                    "country": customer.country,
                    "zip": customer.zip,
                    "last_name": customer.last_name,
                    "first_name": customer.first_name,
                    "phone": customer.phone,
                }
            ],
            "note": customer.note,
            "tags": customer.tags,
        }

        if customer.newsletter:
            customer_data["email_marketing_consent"] = {
                "state": "subscribed",
                "opt_in_level": "confirmed_opt_in",
            }
        if customer.sms:
            customer_data["sms_marketing_consent"] = {
                "state": "subscribed",
                "opt_in_level": "single_opt_in",
            }

        shopify_customer = shopify.Customer(customer_data)

        if shopify_customer.save():

            for metafield in metafields:
                shopify_metafield = shopify.Metafield()
                shopify_metafield.namespace = metafield['namespace']
                shopify_metafield.key = metafield['key']
                shopify_metafield.value = metafield['value']
                shopify_customer.add_metafield(shopify_metafield)

        else:

            print(shopify_customer.errors.full_messages())

            del customer_data['phone']
            for address in customer_data["addresses"]:
                if 'phone' in address:
                    del address['phone']

            shopify_customer = shopify.Customer(customer_data)

            if shopify_customer.save():

                for metafield in metafields:
                    shopify_metafield = shopify.Metafield()
                    shopify_metafield.namespace = metafield['namespace']
                    shopify_metafield.key = metafield['key']
                    shopify_metafield.value = metafield['value']
                    shopify_customer.add_metafield(shopify_metafield)

            else:
                print(shopify_customer.errors.full_messages())

        return shopify_customer


def delete_customer(id, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_customer = shopify.Customer.find(id)

        success = shopify_customer.destroy()

        return success
