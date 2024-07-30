from django.db import models
from django.db.models import Q


class Vendor(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name


class Product(models.Model):
    # Primary
    sku = models.CharField(max_length=200, primary_key=True)
    title = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    handle = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    description = models.TextField(
        max_length=5000, default=None, blank=True, null=True)
    barcode = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    # Category
    vendor = models.ForeignKey(
        Vendor, related_name="products", on_delete=models.CASCADE, blank=False, null=False)
    type = models.ForeignKey(
        Type, related_name="products", on_delete=models.CASCADE, blank=False, null=False)
    tags = models.ManyToManyField(Tag, related_name="products")

    # Pricing
    cost = models.FloatField(default=0, blank=False, null=False)
    price = models.FloatField(default=0, blank=True, null=True)

    # Inventory & Shipping
    quantity = models.IntegerField(default=0, null=True, blank=True)
    weight = models.FloatField(default=1, null=True, blank=True)

    # Status
    status = models.BooleanField(default=True)

    # Variant
    option_name = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    option_value = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    # Attributes
    meta_attributes = models.JSONField(default=dict, blank=True, null=True)

    # Shopify
    product_id = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    variant_id = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    def __str__(self):
        return self.title


class Image(models.Model):
    path = models.CharField(
        max_length=2000, default=None, blank=False, null=False)
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.product.sku


class Customer(models.Model):

    email = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    phone = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    first_name = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    last_name = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    company = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    address1 = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    address2 = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    city = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    state = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    zip = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    country = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    note = models.TextField(
        max_length=2000, default=None, null=True, blank=True)
    tags = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    meta_attributes = models.JSONField(
        default=dict, blank=True, null=True)

    customer_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):

    customer = models.ForeignKey(
        Customer, related_name='orders', on_delete=models.CASCADE, blank=False, null=False)

    order_total = models.FloatField(default=0, null=False, blank=False)
    discount = models.FloatField(default=0, null=False, blank=False)

    shipping_method = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    shipping_cost = models.FloatField(default=0, null=False, blank=False)

    order_date = models.DateField(null=True, blank=True)
    order_note = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    tracking_number = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    meta_attributes = models.JSONField(default=dict, blank=True, null=True)

    order_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def __str__(self):
        return self.order_no


class LineItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='lineItems', on_delete=models.CASCADE, blank=False, null=False)

    product = models.ForeignKey(
        Product, related_name='lineItems', on_delete=models.CASCADE, blank=False, null=False)

    unit_price = models.FloatField(default=0, null=False, blank=False)
    quantity = models.IntegerField(default=1, null=False, blank=False)

    def __str__(self):
        return self.order.order_no
