from pathlib import Path
from django.core.management.base import BaseCommand
from collections import defaultdict
import csv
from vendor.models import Vendor, Order, PurchaseOrderDetail, Product
from utils import shopify
import requests
import os
import json
import time

FILEDIR = f"{Path(__file__).resolve().parent.parent}/files"

ENITURE_API_KEY = os.getenv('ENITURE_API_KEY')


class Command(BaseCommand):
    help = f"Export CSV"

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        processor = Processor()

        if "suppliers" in options['functions']:
            processor.suppliers()

        if "purchase-orders" in options['functions']:
            processor.purchase_orders()

        if "purchase-orders-received" in options['functions']:
            processor.purchase_orders_received()

        if "on-hand-inventory" in options['functions']:
            processor.on_hand_inventory()

        if "shipments" in options['functions']:
            processor.order_shipments(status="Delivered")
            processor.order_shipments(status="Partial Shipment")

        if "eniture" in options['functions']:
            processor.eniture()


class Processor:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def suppliers(self):
        data = []
        data.append([
            "Name",
            "State"
        ])

        suppliers = Vendor.objects.all()

        for supplier in suppliers:
            data.append([
                supplier.name,
                supplier.state,
            ])

        with open(f"{FILEDIR}/suppliers.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def purchase_orders(self):
        data = []
        data.append([
            "PO #",
            "Supplier",
            "Warehouse",
            "Store",
            "Quantity",
            "Rate",
            "SKU",
            "Received",
            "Memo",
            "Arrival date",
            "Status"
        ])

        # Create a dictionary to hold combined results
        combined_data = defaultdict(lambda: {
            "po": "",
            "supplier": "",
            "warehouse": "Default Warehouse",
            "store": "VinsRare Shopify",
            "quantity": 0,
            "rate": 0,
            "sku": "",
            "received": 0,
            "memo": "",
            "arrival_date": "",
            "status": "",
        })

        details = PurchaseOrderDetail.objects.all()
        for detail in details:
            if detail.quantity > 0:
                key = (detail.purchase_order.po_id, detail.product.product_id)

                if combined_data[key]['po'] == "":
                    combined_data[key].update({
                        "po": detail.purchase_order.po_id,
                        "supplier": detail.purchase_order.vendor.name,
                        "rate": detail.cost,
                        "sku": detail.product.product_id,
                        "received": detail.received,
                        "memo": detail.purchase_order.reference,
                        "arrival_date": detail.received_date,
                        "status": "closed" if detail.received_date else "sent"
                    })

                combined_data[key]['quantity'] += detail.quantity

        for item in combined_data.values():
            data.append([
                item['po'],
                item['supplier'],
                item['warehouse'],
                item['store'],
                item['quantity'],
                item['rate'],
                item['sku'],
                item['received'],
                item['memo'],
                item['arrival_date'],
                item['status']
            ])

        with open(f"{FILEDIR}/purchase-orders.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def purchase_orders_received(self):
        data = []
        data.append([
            "PO #",
            "Type",
            "Item SKU or Kit name",
            "Quantity",
            "Warehouse",
            "Location",
            "Receive Quantity",
            "Serial #"
        ])

        # Create a dictionary to hold combined results
        combined_data = defaultdict(lambda: {
            "po": "",
            "type": "Item",
            "sku": "",
            "quantity": 0,
            "warehouse": "Default Warehouse",
            "location": "",
            "received": 0,
            "serial": "",
        })

        details = PurchaseOrderDetail.objects.all()
        for detail in details:
            if detail.quantity > 0 and detail.received > 0:
                key = (detail.purchase_order.po_id, detail.product.product_id)

                if combined_data[key]['po'] == "":
                    combined_data[key].update({
                        "po": detail.purchase_order.po_id,
                        "sku": detail.product.product_id,
                        "received": detail.received,
                    })

                combined_data[key]['quantity'] += detail.quantity

        for item in combined_data.values():
            data.append([
                item['po'],
                item['type'],
                item['sku'],
                item['quantity'],
                item['warehouse'],
                item['location'],
                item['received'],
                item['serial'],
            ])

        with open(f"{FILEDIR}/purchase-orders-received.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def on_hand_inventory(self):
        data = []
        data.append([
            "SKU",
            "On Hand Inventory",
            "PO Received",
            "PO Incoming",
            "Order Shipped",
            "Order Reserved"
        ])

        # Create a dictionary to hold combined results
        combined_data = defaultdict(lambda: {
            "sku": "",
            "on_hand": 0,
            "po_receipts": 0,
            "po_incoming": 0,
            "order_shipped": 0,
            "order_reserved": 0,
        })

        products = Product.objects.all()
        for product in products:

            on_hand = 0
            po_receipts = 0
            po_incoming = 0
            order_shipped = 0
            order_reserved = 0

            lineItems = product.lineItems.all()
            for lineItem in lineItems:
                order_shipped += lineItem.shipped
                order_reserved += (lineItem.quantity - lineItem.shipped)

            purchaseOrderDetails = product.purchaseOrderDetails.all()
            for purchaseOrderDetail in purchaseOrderDetails:
                po_receipts += purchaseOrderDetail.received
                po_incoming += (purchaseOrderDetail.quantity -
                                purchaseOrderDetail.received)

            on_hand = po_receipts - order_shipped

            key = product.product_id

            if combined_data[key]['sku'] == "":
                combined_data[key].update({
                    "sku": key,
                    "on_hand": on_hand,
                    "po_receipts": po_receipts,
                    "po_incoming": po_incoming,
                    "order_shipped": order_shipped,
                    "order_reserved": order_reserved,
                })

        for item in combined_data.values():
            data.append([
                item['sku'],
                item['on_hand'],
                item['po_receipts'],
                item['po_incoming'],
                item['order_shipped'],
                item['order_reserved'],
            ])

        with open(f"{FILEDIR}/on-hand-inventory.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def order_shipments(self, status):
        data = []
        data.append([
            "Store",
            "Order #",
            "Carrier",
            "Service",
            "Tracking #",
            "Cost",
            "SKU",
            "Quantity",
            "Warehouse",
        ])

        # Create a dictionary to hold combined results
        combined_data = defaultdict(lambda: {
            "store": "VinsRare Shopify",
            "po": "",
            "carrier": "Custom",
            "service": "",
            "tracking": "#",
            "cost": 0,
            "sku": "",
            "quantity": 0,
            "warehouse": "Default Warehouse",
        })

        orders = Order.objects.filter(status=status).exclude(
            shopify_id=None).exclude(shopify_order_number=None)
        total = len(orders)
        for index, order in enumerate(orders):
            print(f"{index}/{total}: {order.shopify_order_number}")

            lineItems = order.lineItems.all()
            for lineItem in lineItems:

                sku = lineItem.product.product_id
                quantity = lineItem.shipped

                if sku is not None and quantity > 0:
                    key = (order.order_id, sku)
                    if combined_data[key]['po'] == "":
                        combined_data[key].update({
                            "po": order.shopify_order_number,
                            "service": order.shipping_method or "Ground",
                            "cost": order.shipping_price,
                            "sku": sku,
                            "quantity": quantity,
                        })

        for item in combined_data.values():
            data.append([
                item['store'],
                item['po'],
                item['carrier'],
                item['service'],
                item['tracking'],
                item['cost'],
                item['sku'],
                item['quantity'],
                item['warehouse'],
            ])

        with open(f"{FILEDIR}/{status}.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def eniture(self):
        products = Product.objects.filter(weight__gt=0).filter(width__gt=0)
        print(len(products))

        for product in products:
            
            shopify_product = shopify.get_product(product.shopify_id)
            product_id = shopify_product.id
            variant_id = shopify_product.variants[0].id

            if product_id == 8815497543919:
                continue

            if product_id and variant_id:

                # Check Current
                url = f"https://s-web-api.eniture.com/api/products/{product_id}/{variant_id}"
                print(url)

                headers = {
                    'Accept': 'application/json',
                    'X-Shopify-Shop': '5bebb7-54.myshopify.com',
                    'Authorization': f"Bearer {ENITURE_API_KEY}"
                }
                payload={}

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

                # Upload
                url = "https://s-web-api.eniture.com/api/products"

                payload = json.dumps({
                    "data": {
                        "productId": product_id,
                        "variantId": variant_id,
                        "attributes": {
                            "weight": product.weight,
                            "width": product.width,
                            "height": product.height,
                            "length": product.depth
                        }
                    }
                })
                headers = {
                    'X-Shopify-Shop': '5bebb7-54.myshopify.com',
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {ENITURE_API_KEY}'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.status_code)

                time.sleep(1)
