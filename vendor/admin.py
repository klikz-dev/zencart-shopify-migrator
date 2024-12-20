from django.contrib import admin

from .models import Category, Type, Tag, Product, Address, Customer, Order, LineItem, Vendor, PurchaseOrder, PurchaseOrderDetail


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'product_count'
    ]

    search_fields = [
        'name',
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'product_count'
    ]

    search_fields = [
        'name',
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'product_count'
    ]

    search_fields = [
        'name',
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_id',
        'name',
        'type',
        'price',
        'quantity',
        'weight',
        'status',
        'shopify_id',
    ]

    list_filter = [
        'status',
        'pre_arrival',
        'size',
        'track_quantity',
        'type',
        'categories',
        'tags',
    ]

    search_fields = [
        'product_id',
        'name',
        'description',
        'shopify_id',
    ]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'customer',
    ]

    list_display = [
        'address_id',
        'customer',
        'first_name',
        'last_name',
        'address1',
        'city',
        'state',
        'zip',
        'country',
    ]

    list_filter = [
        'country',
    ]

    search_fields = [
        'address_id',
        'customer__customer_id',
        'first_name',
        'last_name',
        'address1',
    ]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = [
        'customer_id',
        'email',
        'phone',
        'first_name',
        'last_name',
        'newsletter',
        'sms',
        'default_address',
        'shopify_id',
    ]

    list_filter = [
        'newsletter',
        'sms',
        'gender',
        'tags',
    ]

    search_fields = [
        'customer_id',
        'email',
        'phone',
        'first_name',
        'last_name',
        'shopify_id',
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    class LineItemInline(admin.StackedInline):
        model = LineItem
        extra = 0

        autocomplete_fields = [
            'product',
        ]

        fields = [
            'product',
            'unit_price',
            'quantity',
            'shipped',
            'shipped_date',
        ]

    autocomplete_fields = [
        'customer',
    ]

    list_display = [
        'order_id',
        'customer',
        'total_price',
        'shipping_price',
        'tax',
        'shipping_method',
        'order_date',
        'shopify_id',
        'shipping_address_id'
    ]

    list_filter = [
        'status'
    ]

    search_fields = [
        'order_id',
        'shipping_method',
        'shipping_address_id',
        'shopify_id',
    ]

    inlines = [LineItemInline]


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'order',
        'product',
    ]

    list_display = [
        'order',
        'product',
        'unit_price',
        'quantity',
        'shipped',
        'shipped_date',
    ]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'state',
        'purchase_order_count'
    ]

    search_fields = [
        'name',
    ]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):

    class PODetailInline(admin.StackedInline):
        model = PurchaseOrderDetail
        extra = 0

        list_display = [
            'po_detail_id',
            'product',
            'cost',
            'quantity',
            'received',
        ]

    list_display = [
        'po_id',
        'vendor',
        'reference',
        'order_date',
    ]

    list_filter = [
        'vendor'
    ]

    search_fields = [
        'po_id'
    ]

    inlines = [PODetailInline]


@admin.register(PurchaseOrderDetail)
class PurchaseOrderDetailAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'purchase_order',
        'product',
    ]

    list_display = [
        'po_detail_id',
        'purchase_order',
        'product',
        'cost',
        'quantity',
        'received',
        'expected_date',
        'received_date',
    ]

    search_fields = [
        'po_detail_id',
        'product__product_id'
    ]
