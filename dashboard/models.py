from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Vendor(models.Model):
    ReviewUrl = models.CharField(max_length=500, null=False)
    OpenTime = models.CharField(max_length=500, null=True)
    RestaurantId = models.PositiveIntegerField(primary_key=True, editable=False)
    Name = models.CharField(max_length=100, null=True)
    Address = models.CharField(max_length=200, null=True)
    District = models.CharField(max_length=100, null=True)
    City = models.CharField(max_length=50, null=True)
    RestaurantStatus = models.FloatField(null=True)
    Latitude = models.FloatField(null=True)
    Longitude = models.FloatField(null=True)
    TotalReviews = models.FloatField(null=True)
    nExcellentReviews = models.FloatField(null=True)
    nGoodReviews = models.FloatField(null=True)
    nAverageReviews = models.FloatField(null=True)
    nBadReviews = models.FloatField(null=True)
    LocationScore = models.FloatField(null=True)
    PriceScore = models.FloatField(null=True)
    QualityScore = models.FloatField(null=True)
    ServingScore = models.FloatField(null=True)
    SpaceScore = models.FloatField(null=True)
    AvgScore = models.FloatField(null=True)
    TotalPictures = models.FloatField(null=True)
    TotalViews = models.FloatField(null=True)
    TotalSaves = models.FloatField(null=True)
    IsBooking = models.BooleanField(null=True)
    IsDelivery = models.BooleanField(null=True)
    PrepTime = models.CharField(max_length=20, null=True)
    Capacity = models.CharField(max_length=50, null=True)
    LastHourCustomer = models.TextField(null=True)
    ExtraInfo = models.TextField(null=True)
    Active = models.BooleanField(null=True)
    TotalFavourites = models.FloatField(null=True)
    TotalCheckIns = models.FloatField(null=True)
    categories = models.TextField(null=True)
    cuisines = models.CharField(max_length=100, null=True)
    avg = models.FloatField(null=True)
    service_fee = models.FloatField(null=True)
    avg_price = models.FloatField(null=True)
    min_order_value = models.FloatField(null=True)
    min_charge = models.FloatField(null=True) # need pre-process
    minimum_shiping_fee = models.FloatField(null=True) # need pre-process
    is_foody_delivery = models.BooleanField(null=True) # need pre-process
    min_price = models.FloatField(null=True)
    max_price = models.FloatField(null=True)
    min_order_amount = models.TextField(null=True) # need pre-process
    expired = models.TextField(null=True)
    promo_description = models.TextField(null=True)
    promo_code = models.TextField(null=True)
    max_discount_value = models.TextField(null=True) # need pre-process
    max_usage_time = models.TextField(null=True)
    apply_order = models.TextField(null=True)
    all_reviews = models.TextField(null=True)
    seeding_pct = models.TextField(null=True)
    PagePic = models.TextField(null=True)
