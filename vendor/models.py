from django.db import models


class Type(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name


class Category(models.Model):
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
    product_id = models.CharField(max_length=200, primary_key=True)

    # Primary
    name = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    description = models.TextField(
        max_length=5000, default=None, blank=True, null=True)

    # Category
    type = models.ForeignKey(
        Type, related_name="products", on_delete=models.CASCADE)
    categories = models.ManyToManyField(
        Category, related_name="products", blank=True)
    tags = models.ManyToManyField(
        Tag, related_name="products", blank=True)

    # Pricing
    price = models.FloatField(default=0, blank=True, null=True)

    # Inventory & Shipping
    quantity = models.IntegerField(default=0, null=True, blank=True)
    weight = models.FloatField(default=1, null=True, blank=True)

    # Status
    status = models.BooleanField(default=True)
    track_quantity = models.BooleanField(default=True)

    # Images
    thumbnail = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    roomset = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    # Meta
    min_order_qty = models.IntegerField(default=0, null=True, blank=True)
    order_increment = models.IntegerField(default=0, null=True, blank=True)

    pre_arrival = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    vintage = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    varietal = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    region = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    sub_region = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    vineyard = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    size = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    disgorged = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    dosage = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    alc = models.CharField(max_length=200, default=None, blank=True, null=True)

    # Shopify
    shopify_id = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    address_id = models.IntegerField(primary_key=True)

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


class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)

    email = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    phone = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    first_name = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    last_name = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    gender = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    address = models.ForeignKey(
        Address, related_name='customers', on_delete=models.CASCADE)

    note = models.TextField(
        max_length=2000, default=None, null=True, blank=True)
    tags = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    newsletter = models.BooleanField(default=True)
    sms = models.BooleanField(default=True)

    shopify_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)

    customer = models.ForeignKey(
        Customer, related_name='orders', on_delete=models.CASCADE, blank=False, null=False)

    total_price = models.FloatField(default=0, null=False, blank=False)
    shipping_price = models.FloatField(default=0, null=False, blank=False)
    tax = models.FloatField(default=0, null=False, blank=False)

    shipping_method = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    tracking_number = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    order_note = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    status = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    shopify_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def __str__(self):
        return self.customer.email


class LineItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='lineItems', on_delete=models.CASCADE, blank=False, null=False)

    product = models.ForeignKey(
        Product, related_name='lineItems', on_delete=models.CASCADE, blank=False, null=False)

    unit_price = models.FloatField(default=0, null=False, blank=False)
    quantity = models.IntegerField(default=1, null=False, blank=False)

    def __str__(self):
        return self.order.customer.email
