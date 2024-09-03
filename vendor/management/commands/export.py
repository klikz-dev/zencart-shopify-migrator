from pathlib import Path
from django.core.management.base import BaseCommand
from collections import defaultdict
import csv
from vendor.models import Vendor, PurchaseOrder, PurchaseOrderDetail

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
            "store": "Shopify",
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
