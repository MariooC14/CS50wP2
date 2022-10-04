from distutils.command.upload import upload
from queue import Empty
from django.contrib.auth.models import AbstractUser
from django.db import models
from .listing_categories import LISTING_CATEGORIES

# One Model per SQL Table

# MODELS:
"""
    Users (Done)
    Listings
    Bids
    Comments on listings (On the page for each listing, not index)
"""

class User(AbstractUser):
    pass

class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=30, blank=False)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(default=10, decimal_places=2, max_digits=10)
    photo_url = models.URLField(max_length=100, blank=True)
    # The field below uses the User's Primary key to as its own key.
    lister = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"'{self.title}' from {self.lister}"
    
    # TODO
    category = models.CharField(choices=LISTING_CATEGORIES,
                                max_length=12,
                                default="NONE")
    
# TODO PUT 2 FOREIGN KEYS
class Bid(models.Model):
    bid_id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bid_for = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10)
    
    def __str__(self):
        return f"{self.bid} for {self.bid_for} placed by {self.bidder}"
    
# TODO ASSIGN KEYS FOR 1. LISTING FOR and 2. Commented by 
class Comment(models.Model) :
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_for = models.ForeignKey(Listing, on_delete=models.CASCADE)
    
"""
class WatchList(models.Model):
    ManyToMany shit or smtn
""" 