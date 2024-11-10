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

    pre_arrival = models.BooleanField(default=False)

    warehouse_location = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    year = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    country = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    appellation = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_ws = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_wa = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_vm = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_bh = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_jg = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_js = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    additional_notes = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    size = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    wine_searcher = models.BooleanField(default=False)
    cellar_tracker_id = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    varietal = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    region = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    sub_region = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    vineyard = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    disgorged = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    dosage = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    alc = models.CharField(max_length=200, default=None, blank=True, null=True)
    biodynamic = models.BooleanField(default=False)
    rating_jd = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_jm = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_wh = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    rating_vr = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    depth = models.FloatField(default=0, null=False, blank=False)
    width = models.FloatField(default=0, null=False, blank=False)
    height = models.FloatField(default=0, null=False, blank=False)

    # Shopify
    shopify_id = models.CharField(
        max_length=200, default=None, blank=True, null=True)

    def __str__(self):
        return self.name


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

    note = models.TextField(
        max_length=2000, default=None, null=True, blank=True)
    tags = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    newsletter = models.BooleanField(default=True)
    sms = models.BooleanField(default=True)

    default_address = models.IntegerField(default=None, null=True, blank=True)

    shopify_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def __str__(self):
        return str(self.customer_id)


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

    customer = models.ForeignKey(
        Customer, related_name='addresses', on_delete=models.CASCADE)


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

    billing_name = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_company = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_address1 = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_address2 = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_city = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_state = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_zip = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    billing_country = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    status = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    shipping_address_id = models.IntegerField(
        default=None, null=True, blank=True)

    shopify_id = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    shopify_order_number = models.CharField(
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
    shipped = models.IntegerField(default=1, null=False, blank=False)
    shipped_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.order.customer.email


class Vendor(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    state = models.CharField(
        max_length=200, default=None, null=True, blank=True)

    def purchase_order_count(self):
        return self.purchaseOrders.count()

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    po_id = models.IntegerField(primary_key=True)

    vendor = models.ForeignKey(
        Vendor, related_name="purchaseOrders", on_delete=models.CASCADE)

    reference = models.CharField(
        max_length=200, default=None, null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)


class PurchaseOrderDetail(models.Model):
    po_detail_id = models.IntegerField(primary_key=True)

    purchase_order = models.ForeignKey(
        PurchaseOrder, related_name="details", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='purchaseOrderDetails', on_delete=models.CASCADE, blank=False, null=False)

    cost = models.FloatField(default=0, blank=True, null=True)

    quantity = models.IntegerField(default=0, null=True, blank=True)
    received = models.IntegerField(default=0, null=True, blank=True)

    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
