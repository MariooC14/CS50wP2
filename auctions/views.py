from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve
import logging

from .models import User, Listing, Comment, Bid
from .forms import BidForm

logging.basicConfig(level=logging.INFO)

def index(request):
    listings = Listing.objects.filter(active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings 
    })

def listing(request, listing_id):
    
    bid_count = Bid.objects.filter(bid_for=Listing.objects.get(pk=listing_id)).annotate(Count('bid'))
    
    try:
        current_listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "listing": None
        })
        
    # Fetch comments
    comments = Comment.objects.filter(comment_for=Listing.objects.get(pk=listing_id))
    
    if request.method == "POST":
        
        message = ''
        form = BidForm(request.POST)
        
        if form.is_valid():
            
            bid = form.cleaned_data["bid"]
            
            # The try except below might have a redundancy.
            try: 
                highest_bid = Bid.objects.filter(bid_for=current_listing).latest('bid').bid
            except Bid.DoesNotExist:
                highest_bid = current_listing.price
            
            if bid > highest_bid:

                # Store new bid into db
                new_bid = Bid(bidder=request.user, bid=bid, bid_for=current_listing)
                new_bid.save()
                
                # Update price of listing
                current_listing.price = bid
                current_listing.save()
                message="Success! You have placed your new bid."
            else:
                message = "Bid must be higher than the current bid."
            
        else:
            message = "Invalid Bid"
            
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": current_listing,
            "comments": comments,
            "bid_count": len(bid_count),
            "message": message,
        })
        
    else:
        form = BidForm()
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": current_listing,
            "comments": comments,
            "bid_count": len(bid_count),
    }) 
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
