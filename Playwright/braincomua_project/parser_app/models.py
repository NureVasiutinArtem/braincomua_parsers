# from django.db import models

# # Create your models here.
# class Product(models.Model):
#     title = models.CharField(max_length=255)
#     producer = models.CharField(max_length=100, blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     red_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
#     color = models.CharField(max_length=100, blank=True, null=True)
#     memory = models.CharField(max_length=50, blank=True, null=True)
#     art = models.CharField(max_length=50, blank=True, null=True)
#     diagonal = models.CharField(max_length=50, blank=True, null=True)
#     display = models.CharField(max_length=50, blank=True, null=True)
#     product_code = models.CharField(max_length=50, unique=True)
#     comment_count = models.IntegerField(default=0)
#     images = models.JSONField(blank=True, null=True)
#     description = models.JSONField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
from django.db import models

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255)
    producer = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    red_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    memory = models.CharField(max_length=50, blank=True, null=True)
    art = models.CharField(max_length=50, blank=True, null=True)
    diagonal = models.CharField(max_length=50, blank=True, null=True)
    display = models.CharField(max_length=50, blank=True, null=True)
    product_code = models.CharField(max_length=50, null=True)
    comment_count = models.IntegerField(default=0,null=True)
    images = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
