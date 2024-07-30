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
    class ImageInline(admin.StackedInline):
        model = Image
        extra = 0

        fields = [
            'path',
        ]

    list_display = [
        'sku',
        'title',
        'cost',
        'price',
        'option_name',
        'option_value',
        'product_id',
        'variant_id',
    ]

    list_filter = [
        'type__name',
        'status',
        'tags',
    ]

    search_fields = [
        'sku',
        'title',
        'handle',
        'description',
        'barcode',
        'product_id',
        'variant_id',
    ]

    inlines = [ImageInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    autocomplete_fields = [
        'product',
    ]

    list_display = [
        'path',
        'product',
    ]

    list_filter = [
        'product__type__name',
    ]

    search_fields = [
        'path',
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
        'customer_id'
    ]

    list_filter = [
        'country',
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
