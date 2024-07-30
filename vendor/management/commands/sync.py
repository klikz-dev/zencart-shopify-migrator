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
                    product_id=product.product_id,
                    image=image,
                    alt=product.name,
                    thread=index
                )
                print(
                    f"Uploaded Image {shopify_image.id} for Product {product.product_id}")

            except Exception as e:
                print(e)
                return

        for index, image in enumerate(images):
            sync_image(index, image)

    def products(self):

        products = Product.objects.filter(product_id=None)
        total = len(products)

        def sync_product(index, product):
            try:
                shopify_product = shopify.create_product(
                    product=product, thread=index)

                if shopify_product.id:
                    product.product_id = shopify_product.id
                    product.save()

                    self.image(product)

                    print(
                        f"{index}/{total} -- Product {shopify_product.id} has been created successfully.")

                    shopify.update_inventory(product=product, thread=index)
                else:
                    print(
                        f"Failed uploading - Product {product.sku}")

            except Exception as e:
                print(e)
                return

        # for index, product in enumerate(products):
        #     sync_product(index, product)

        common.thread(rows=products, function=sync_product)
