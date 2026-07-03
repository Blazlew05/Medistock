from django.db import models


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100, db_index=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    unidad = models.CharField(max_length=50, default="unidad")
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    requiere_receta = models.BooleanField(default=False)
    es_critico = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    @property
    def stock_total(self):
        return sum(stock.cantidad for stock in self.stocks.all())

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Bodega(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    region = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class StockBodega(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="stocks")
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name="stocks")
    cantidad = models.IntegerField(default=0)
    lote = models.CharField(max_length=100, blank=True, null=True)
    caducidad = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("producto", "bodega")

    def __str__(self):
        return f"{self.producto.codigo} @ {self.bodega.nombre}: {self.cantidad}"
