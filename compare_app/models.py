from django.db import models
from django.db.models import IntegerField
from django.db.models.functions import Cast

class pricings(models.Model):
    
    NAME = models.CharField(max_length=200)
    WEIGHT = models.CharField(max_length=80) 
    OZ = models.FloatField() 
    PRICE_TEXT = models.CharField(max_length=20)
    PRICE = models.FloatField()
    PRICE_PER_OZ = models.CharField(max_length=20) 
    CURRENCY = models.CharField(max_length=10)
    AVAILABILITY = models.CharField(max_length=200)
    LINK = models.CharField(max_length=300)
    LOAD_TIME = models.CharField(max_length=30)
    SHOP = models.CharField(max_length=40)
    IMG_LINK = models.CharField(max_length=300)
    METAL = models.CharField(max_length=50)
    PRICE_PLN = models.CharField(max_length=20)
    PRICE_PER_OZ_PLN = models.CharField(max_length=20) 

class v_pricenew(models.Model):
    NAME = models.CharField(max_length=200)
    WEIGHT = models.CharField(max_length=80) 
    OZ = models.FloatField() 
    PRICE_TEXT = models.CharField(max_length=20)
    PRICE = models.FloatField()
    PRICE_PER_OZ = models.CharField(max_length=20) 
    CURRENCY = models.CharField(max_length=10)
    LINK = models.CharField(max_length=300)
    LOAD_TIME = models.CharField(max_length=30)
    SHOP = models.CharField(max_length=40)
    IMG_LINK = models.CharField(max_length=300)
    METAL = models.CharField(max_length=50)
    PRICE_PLN = models.CharField(max_length=20)
    PRICE_PER_OZ_PLN = models.CharField(max_length=20) 
    class Meta:
        managed = False
        db_table = 'compare_app_v_pricenew' 

