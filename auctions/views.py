import pkgutil
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve
import logging

from .models import User, Listing, Comment, Bid
from .forms import BidForm

logger = logging.getLogger(__name__)

def index(request):
    listings = Listing.objects.filter(active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings 
    })

def listing(request, listing_id):
    
    logging.info(listing_id)
    
    bid_count = Bid.objects.filter(bid_for=Listing.objects.get(pk=listing_id)).annotate(Count('bid'))
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "listing": None
        })
        
    comments = Comment.objects.filter(comment_for=Listing.objects.get(pk=listing_id))
    
    if request.method == "POST":
        message = ''
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            try: 
                highest_bid = Bid.objects.filter(bid_for=Listing.objects.get(pk=listing_id)).latest('bid')
                logger.info(highest_bid)
            except Bid.DoesNotExist:
                highest_bid = Listing.objects.get(
                    id=Listing.objects.get(pk=listing_id)).price
            
            if bid > highest_bid:
                # Process the bid
                new_bid = Bid(bidder=request.user, bid=bid, bid_for=Listing.objects.get(pk=listing_id))
                new_bid.save()
                
                listing1 = Listing.objects.get(pk=listing_id)
                listing1.price = bid
                listing1.save()
                message="Success! You have placed your new bid."
            else:
                message = "Bid must be higher than the current bid."
            
        else:
            message = "Invalid Bid"
            
        listing = Listing.objects.get(pk=listing_id)
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": listing,
            "comments": comments,
            "bid_count": len(bid_count),
            "message": message,
        })
        
    else:
        form = BidForm()
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": listing,
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
