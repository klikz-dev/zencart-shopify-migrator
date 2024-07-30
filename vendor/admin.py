from django.contrib import admin

from .models import Vendor, Type, Tag, Product, Image, Customer, Order, LineItem


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'product_count'
    ]

    search_fields = [
        'name',
    ]


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):

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
        'sku',
        'name',
        'type',
        'category',
        'price',
        'quantity',
        'weight',
        'status',
        'product_id',
        'variant_id',
    ]

    list_filter = [
        'type',
        'category',
        'status',
        'track_quantity',
    ]

    search_fields = [
        'sku',
        'name',
        'description',
        'product_id',
        'variant_id',
    ]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = [
        'email',
        'phone',
        'first_name',
        'last_name',
        'address1',
        'city',
        'state',
        'zip',
        'country',
        'newsletter',
        'sms',
        'customer_id'
    ]

    list_filter = [
        'country',
        'newsletter',
        'sms',
        'gender',
        'tags'
    ]

    search_fields = [
        'email',
        'phone',
        'first_name',
        'last_name',
        'customer_id',
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
            'item_note',
        ]

    autocomplete_fields = [
        'customer',
    ]

    list_display = [
        'customer',
        'shipping_cost',
        'shipping_method',
        'order_total',
        'order_date',
        'order_id',
    ]

    search_fields = [
        'shipping_method',
        'order_id',
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
    ]
