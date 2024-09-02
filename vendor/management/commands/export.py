from pathlib import Path
from django.core.management.base import BaseCommand
import csv
from vendor.models import Vendor, PurchaseOrder, PurchaseOrderDetail

FILEDIR = f"{Path(__file__).resolve().parent.parent}/files"


class Command(BaseCommand):
    help = f"Export CSV"

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        processor = Processor()

        if "purchase-orders" in options['functions']:
            processor.purchase_orders()


class Processor:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

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
            "Arrival date"
        ])

        details = PurchaseOrderDetail.objects.all()
        for detail in details:
            data.append([
                detail.purchase_order.po_id,
                detail.purchase_order.vendor.name,
                "Default Warehouse",
                "Shopify",
                detail.quantity,
                detail.cost,
                detail.product.product_id,
                detail.received,
                detail.purchase_order.reference,
                detail.received_date
            ])

        with open(f"{FILEDIR}/purchase-orders.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
