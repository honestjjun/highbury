from django.contrib import admin
from .models import Category, Product, ProductCategory, FantasyLeague, Discount, UsePoint


class ProductCategoryTable(admin.StackedInline):
    model = ProductCategory
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'is_active')
    search_fields = ('name',)

    inlines = [ProductCategoryTable]


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created', 'is_active')
    search_fields = ('name', 'category')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'main_category', 'category', 'point', 'width', 'created', 'is_active')
    search_fields = ('title', 'category', 'width')

    prepopulated_fields = {'title': ('slug',)}


@admin.register(FantasyLeague)
class FantasyLeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created', 'position', 'strategy', 'player')
    search_fields = ('name', 'player')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'start_date', 'end_date', 'discount_point', 'is_active')
    search_fields = ('name',)


@admin.register(UsePoint)
class UsePointAdmin(admin.ModelAdmin):
    list_display = ('product_category', 'product', 'user', 'use_point', 'buy_date', 'order_number')
    search_fields = ('product', 'user')
