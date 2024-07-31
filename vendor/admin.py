from django.contrib import admin

from .models import Category, Type, Tag, Product, Address, Customer, Order, LineItem


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
        'category',
        'price',
        'quantity',
        'weight',
        'status',
        'shopify_id',
    ]

    list_filter = [
        'status',
        'track_quantity',
        'type',
        'category',
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

    list_display = [
        'address_id',
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
        'first_name',
        'last_name',
        'address1',
    ]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'address',
    ]

    list_display = [
        'customer_id',
        'email',
        'phone',
        'first_name',
        'last_name',
        'address',
        'newsletter',
        'sms',
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
            'item_note',
        ]

    autocomplete_fields = [
        'customer',
    ]

    list_display = [
        'customer',
        'total_price',
        'shipping_price',
        'tax',
        'shipping_method',
        'order_date',
        'order_id',
    ]

    list_filter = [
        'status'
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
