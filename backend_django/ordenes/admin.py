from django.contrib import admin

from .models import ItemOrden, Orden


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "estado", "urgencia", "total", "aprobada_por_ejecutivo", "creada_en")
    list_filter = ("estado", "urgencia", "tipo_despacho", "aprobada_por_ejecutivo")
    search_fields = ("numero", "cliente__email")
    inlines = [ItemOrdenInline]
