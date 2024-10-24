from pathlib import Path
from django.core.management.base import BaseCommand
from collections import defaultdict
import csv
from vendor.models import Vendor, Order, PurchaseOrderDetail

FILEDIR = f"{Path(__file__).resolve().parent.parent}/files"


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

        if "shipment" in options['functions']:
            processor.order_shipments()


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
            "received": "",
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

    def order_shipments(self):
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

        orders = Order.objects.all().filter(order_id=41639)
        for order in orders:
            lineItems = order.lineItems.all()
            for lineItem in lineItems:
                sku = lineItem.product.product_id
                quantity = lineItem.shipped
                
                if sku is not None and quantity > 0:
                    key = (order.order_id, sku)
                    if combined_data[key]['po'] == "":
                        combined_data[key].update({
                            "po": order.order_id,
                            "service": order.shipping_method,
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

        with open(f"{FILEDIR}/order-shipments.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
