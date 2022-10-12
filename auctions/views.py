from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import logging

from .models import User, Listing, Comment, Bid, Watchlist
from .forms import BidForm, ListingForm

logging.basicConfig(level=logging.INFO)

def index(request):
    listings = Listing.objects.filter(active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist_count": Watchlist.objects.filter(watched_by=request.user).count() if request.user.is_authenticated else None,
    })

@login_required(login_url="/login")
def listing(request, listing_id):
    
    bid_count = Bid.objects.filter(bid_for=Listing.objects.get(pk=listing_id)).annotate(Count('bid'))
    
    watchlist_count = Watchlist.objects.filter(watched_by=request.user).count()
    
    try:
        current_listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "listing": None,
            "watchlist_count": watchlist_count 
        })
        
    # Fetch comments
    comments = Comment.objects.filter(comment_for=Listing.objects.get(pk=listing_id))
    
    if request.method == "POST":
        
        message = ''
        form = BidForm(request.POST)
        
        if form.is_valid() and current_listing.active == True:
            
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
            message = "Bid is closed"
            
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": current_listing,
            "comments": comments,
            "bid_count": len(bid_count),
            "message": message,
            "watchlist_count": Watchlist.objects.filter(watched_by=request.user).count()
        })
        
    else:
        form = BidForm()
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": current_listing,
            "comments": comments,
            "bid_count": len(bid_count),
            "watchlist_count": Watchlist.objects.filter(watched_by=request.user).count(),
    }) 
    

@login_required(login_url='/login')
def createListing(request):
    
    if request.method == "POST":
        # Get Form
        form = ListingForm(request.POST)
        
        # Validate Form
        if form.is_valid():
            
            form = form.cleaned_data
            new_listing = Listing(title=form['title'],
                                description=form['description'],
                                price=form["price"],
                                photo_url=form['photo_url'],
                                lister=request.user)
            new_listing.save()

            return HttpResponseRedirect(reverse('index'))
        
    else:
        return render(request, "auctions/create_listing.html", {
            'form': ListingForm,
            "watchlist_count": Watchlist.objects.filter(watched_by=request.user).count(),
        })


@login_required(login_url="/login")
def closeListing(request, listing_id):
    # Close Listing if the user is the lister
    if request.method == "GET":
        try:
            current_listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            return HttpResponseRedirect('')
        
        if current_listing.lister != request.user:
            return HttpResponseRedirect('')
        
        else:
            
            current_listing.active = False
            
            try:
                highest_bidder = Bid.objects.filter(bid_for=current_listing).latest('bid').bidder
            except Bid.DoesNotExist:
                return redirect('/')
                
            
            current_listing.winner = highest_bidder
            current_listing.save()
            return redirect(f'/listings/{listing_id}')   

@login_required(login_url='/login')
def watchlist(request):
    # Get ids of the listings watched by the user
    watchlist_pks = Watchlist.objects.filter(watched_by=request.user).values_list('listing', flat=True)
    if watchlist_pks:
        # Get listings whose id are IN the watchlist id list.
        listings = Listing.objects.filter(id__in=watchlist_pks)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings,
        "watchlist_count": len(listings),
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
