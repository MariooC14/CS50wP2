from django.contrib.auth.models import AbstractUser
from django.db import models
from .listing_categories import LISTING_CATEGORIES

# One Model per SQL Table

# MODELS:
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
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='winner')
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    category = models.CharField(choices=LISTING_CATEGORIES,
                                max_length=12,
                                default="NONE")

    def __str__(self):
        return f"'{self.title}' from {self.lister}"
 

class Bid(models.Model):
    bid_id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bid_for = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10)
    
    def __str__(self):
        return f"{self.bid} for {self.bid_for} placed by {self.bidder}"

class Watchlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    watched_by = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="listing", on_delete=models.CASCADE)



class Comment(models.Model) :
    id = models.AutoField(primary_key=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_for = models.ForeignKey(Listing, on_delete=models.CASCADE)