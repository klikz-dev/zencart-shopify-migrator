import os
import base64
from pathlib import Path
import shopify
import json
from vendor.models import Address, Product, Order

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
            'biodynamic',
            'rating_jd',
            'rating_jm',
            'rating_wh',
            'rating_vr',

            'depth',
            'width',
            'height',
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
            'sku': product.product_id,
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

    def generate_order_metafields(self, order):
        metafield_keys = [
            'order_id',
        ]

        metafields = []
        for metafield_key in metafield_keys:
            metafield_value = getattr(order, metafield_key)

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


def update_product(product, thread=None):

    processor = Processor(thread=thread)

    metafields = processor.generate_product_metafields(product=product)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_product = shopify.Product.find(product.shopify_id)

        if not shopify_product:
            print(f"Product with ID {product.shopify_id} does not exist.")
            return None

        existing_metafields = shopify_product.metafields()

        for metafield in metafields:
            for existing_metafield in existing_metafields:
                if existing_metafield.key == metafield['key']:
                    existing_metafield.value = metafield['value']
                    existing_metafield.save()
                    break

        return shopify_product


def product_status(thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_products = shopify.Product.find(limit=250)

        active = 0
        draft = 0
        archived = 0

        while shopify_products:

            print(f"Fetched {len(shopify_products)} Products")

            for shopify_product in shopify_products:
                try:
                    product = Product.objects.get(shopify_id=shopify_product.id)
                    if not product.status:
                        lineItems = product.lineItems.filter(order__status__in=["Partial Shipment", "Pending", "Processing"])
                        if len(lineItems) > 0:
                            status = "draft"
                            draft += 1
                        else:
                            status = "archived"
                            archived += 1
                    else:
                        status = "active"
                        active += 1
                except Product.DoesNotExist:
                    status = "archived"
                    archived += 1

                try:
                    shopify_product.status = status
                    shopify_product.save()

                    print(f"Updated {shopify_product.handle} status to {status}")
                except Exception as e:
                    print(e)

            shopify_products = shopify_products.has_next_page(
            ) and shopify_products.next_page() or []

        print(f"Active: {active}, Draft: {draft}, Archived: {archived}")



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

        # Exceptions
        email = customer.email.replace(" ", "")

        addresses = []
        for address in customer.addresses.all():
            address_obj = {
                "first_name": address.first_name,
                "last_name": address.last_name,
                "company": address.company,
                "address1": address.address1,
                "address2": address.address2,
                "city": address.city,
                "province": address.state,
                "zip": address.zip,
                "country": address.country,
            }
            if address.address_id == customer.default_address:
                address_obj['default'] = True

            addresses.append(address_obj)

        customer_data = {
            "email": email,
            "phone": customer.phone,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "addresses": addresses,
            "note": customer.note,
            "tags": customer.tags,
        }

        if customer.newsletter:
            customer_data["email_marketing_consent"] = {
                "state": "subscribed",
                "opt_in_level": "confirmed_opt_in",
            }
        if customer.sms and customer.phone:
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

            print(f"{customer}: {shopify_customer.errors.full_messages()}")

            if 'phone' in customer_data:
                del customer_data['phone']
                customer.phone = None
                customer.save()
            if 'sms_marketing_consent' in customer_data:
                del customer_data['sms_marketing_consent']

            shopify_customer = shopify.Customer(customer_data)

            if shopify_customer.save():

                for metafield in metafields:
                    shopify_metafield = shopify.Metafield()
                    shopify_metafield.namespace = metafield['namespace']
                    shopify_metafield.key = metafield['key']
                    shopify_metafield.value = metafield['value']
                    shopify_customer.add_metafield(shopify_metafield)

            else:
                print(f"{customer}: {shopify_customer.errors.full_messages()}")

        return shopify_customer


def delete_customer(id, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_customer = shopify.Customer.find(id)

        success = shopify_customer.destroy()

        return success


def list_orders(thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        all_shopify_order_ids = []
        shopify_orders = shopify.Order.find(limit=250, status="any")

        while shopify_orders:

            print(f"Fetched {len(shopify_orders)} Orders.")

            for shopify_order in shopify_orders:
                all_shopify_order_ids.append(shopify_order.id)

            shopify_orders = shopify_orders.has_next_page(
            ) and shopify_orders.next_page() or []

        return all_shopify_order_ids


def get_order(id, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_order = shopify.Order.find(id)
        return shopify_order


def create_order(order, thread=None):
    processor = Processor(thread=thread)

    # metafields = processor.generate_order_metafields(order=order)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_order = shopify.Order()

        # Customer
        shopify_order.customer = {
            "id": order.customer.shopify_id
        }
        shopify_order.phone = order.customer.phone

        # Line Items
        line_items = []
        for item in order.lineItems.all():
            try:
                shopify_product = shopify.Product.find(item.product.shopify_id)
                variant_id = shopify_product.variants[0].id
            except Exception as e:
                print(e)
                continue

            line_item = shopify.LineItem({
                "variant_id": variant_id,
                "price": item.unit_price,
                "quantity": item.quantity,
            })
            line_items.append(line_item)
        shopify_order.line_items = line_items

        # Costs
        if not order.shipping_price < 0:
            shopify_order.shipping_lines = [{
                "title": order.shipping_method or "FedEx",
                "price": order.shipping_price
            }]
        shopify_order.tax_lines = [{
            'price': order.tax
        }]
        shopify_order.total_price = order.total_price
        if order.order_date:
            shopify_order.created_at = order.order_date.isoformat()

        # Shipping Address
        if order.shipping_address_id:
            try:
                shipping_address = Address.objects.get(
                    address_id=order.shipping_address_id)

                shopify_order.shipping_address = {
                    'first_name': shipping_address.first_name,
                    'last_name': shipping_address.last_name,
                    'company': shipping_address.company,
                    'address1': shipping_address.address1,
                    'address2': shipping_address.address2,
                    'city': shipping_address.city,
                    'province': shipping_address.state,
                    'zip': shipping_address.zip,
                    'country': shipping_address.country,
                    'phone': shipping_address.customer.phone
                }
            except Exception as e:
                print(e)
                pass

        # Billing Address
        shopify_order.billing_address = {
            'name': order.billing_name,
            'company': order.billing_company,
            'address1': order.billing_address1,
            'address2': order.billing_address2,
            'city': order.billing_city,
            'province': order.billing_state,
            'zip': order.billing_zip,
            'country': order.billing_country,
        }

        # Order Status
        if order.status == "Cancelled":
            shopify_order.fulfillment_status = "restocked"
            shopify_order.financial_status = "refunded"
        elif order.status == "Delivered":
            shopify_order.financial_status = "paid"
        elif order.status == "Partial Shipment":
            shopify_order.financial_status = "paid"
        elif order.status == "Pending":
            shopify_order.financial_status = "pending"
        elif order.status == "Processing":
            shopify_order.financial_status = "paid"
        else:
            shopify_order.financial_status = "pending"

        # Order Note
        shopify_order.note = f"Zencart Order ID: {order.order_id}"

        # Metafields
        if shopify_order.save():
            # for metafield in metafields:
            #     shopify_metafield = shopify.Metafield()
            #     shopify_metafield.namespace = metafield['namespace']
            #     shopify_metafield.key = metafield['key']
            #     shopify_metafield.value = metafield['value']
            #     shopify_order.add_metafield(shopify_metafield)
            
            pass

        else:
            print(shopify_order.errors.full_messages())

        return shopify_order

    
def fulfill_order(order, thread=None):
    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        graphQL = shopify.GraphQL()

        fo = [fo for fo in shopify.FulfillmentOrders.find(order_id=order.shopify_id) if fo.status == "open" or fo.status == "in_progress"][0]

        mutation = """
            mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!) {
                fulfillmentCreateV2(fulfillment: $fulfillment) {
                    fulfillment {
                        id
                        status
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
        """

        fulfillmentOrderLineItems = []
        shipped_date = None
        for foLineItem in fo.line_items:
            variant = shopify.Variant.find(foLineItem.variant_id)

            for lineItem in order.lineItems.all():
                sku = lineItem.product.product_id

                if lineItem.shipped > 0 and sku == variant.sku:
                    fulfillmentOrderLineItems.append({
                        'id': f"gid://shopify/FulfillmentOrderLineItem/{foLineItem.id}",
                        'quantity': lineItem.shipped
                    })
                    shipped_date = lineItem.shipped_date
                    break

        if len(fulfillmentOrderLineItems) > 0:

            graphql_response = graphQL.execute(mutation, variables={
                "fulfillment": {
                    "lineItemsByFulfillmentOrder": {
                        "fulfillmentOrderId": f"gid://shopify/FulfillmentOrder/{fo.id}",
                        "fulfillmentOrderLineItems": fulfillmentOrderLineItems
                    },
                    "notifyCustomer": False,
                }
            })
            response = json.loads(graphql_response)

            fulfillment = response['data']['fulfillmentCreateV2']['fulfillment']

            print(fulfillment)

            # fulfillment Event
            mutation = """
                mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
                    fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
                        fulfillmentEvent {
                            id
                            status
                            message
                        }
                        userErrors {
                            field
                            message
                        }
                    }
                }
            """
            graphql_response = graphQL.execute(mutation, variables={
                "fulfillmentEvent": {
                    "fulfillmentId": fulfillment['id'],
                    "status": "DELIVERED",
                    "happenedAt": shipped_date.isoformat() if shipped_date else None
                }
            })
            response = json.loads(graphql_response)

            fulfillmentEvent = response['data']['fulfillmentEventCreate']['fulfillmentEvent']

            print(fulfillmentEvent)

            return fulfillment

        else:
            return None


def delete_order(id, thread=None):

    processor = Processor(thread=thread)

    with shopify.Session.temp(SHOPIFY_API_BASE_URL, SHOPIFY_API_VERSION, processor.api_token):

        shopify_order = shopify.Order.find(id)

        success = shopify_order.destroy()

        return success
