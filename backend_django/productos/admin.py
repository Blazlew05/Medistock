from django.contrib import admin

from .models import Bodega, Producto, StockBodega


class StockBodegaInline(admin.TabularInline):
    model = StockBodega
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "precio", "stock_total", "activo")
    list_filter = ("categoria", "activo", "requiere_receta", "es_critico")
    search_fields = ("codigo", "nombre")
    inlines = [StockBodegaInline]


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "region", "activa")
    inlines = [StockBodegaInline]
