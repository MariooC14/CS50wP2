from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import logging
from .listing_categories import LISTING_CATEGORIES

from .models import User, Listing, Comment, Bid, Watchlist
from .forms import BidForm, ListingForm, CommentForm, WatchlistForm

logging.basicConfig(level=logging.INFO)

def index(request):

    listings = Listing.objects.filter(active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist_count": Watchlist.objects.filter(watched_by=request.user).count() if request.user.is_authenticated else None,
    })


def listingsByCategories(request):

    if request.method == "GET":
        # LISTING_CATEGORIES is a list, where each item is a list of the category in uppercase and Title case. We are only getting the Title Case for each
        categories = [category[1] for category in LISTING_CATEGORIES]
        categories.insert(0, "Any")

        # categories are stored in the server in uppercase.
        chosen_category = request.GET.get('category', '').upper()
        logging.info(chosen_category)

        #None means no filter
        if chosen_category == "ANY" or not chosen_category:
            listings = Listing.objects.filter(active=True)
        else:
            listings = Listing.objects.filter(active=True, category=chosen_category)
        return render(request, "auctions/listingsByCategory.html",{
            "categories": categories,
            "listings": listings,
        })



# @login_required(login_url="/login")
def listing(request, listing_id):
    
    bid_count = Bid.objects.filter(bid_for=Listing.objects.get(pk=listing_id)).annotate(Count('bid'))
    try:
        watchlist_count = Watchlist.objects.filter(watched_by=request.user).count()
    except:
        watchlist_count = 0

    try:
        current_listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "listing": None,
            "watchlist_count": watchlist_count 
        })
    try: 
        is_watched = True if Watchlist.objects.filter(
            watched_by=request.user, 
            listing=current_listing) else False
    except:
        is_watched = False
        
    # Fetch comments and initialise comment_form
    comments = Comment.objects.filter(comment_for=Listing.objects.get(pk=listing_id))
    comment_form = CommentForm(initial={"listing_id": listing_id})
    
    watchlist_form = WatchlistForm(initial={"listing_id": listing_id})
    
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
            "comment_form": comment_form,
            "bid_count": len(bid_count),
            "is_watched": is_watched,
            "message": message,
            "watchlist_count": watchlist_count,
            "watchlist_form": watchlist_form,
        })
        
    else:
        form = BidForm()
        return render(request, "auctions/listing.html", {
            "form": BidForm,
            "listing": current_listing,
            "comments": comments,
            "comment_form": comment_form,
            "bid_count": len(bid_count),
            "is_watched": is_watched,
            "watchlist_count": watchlist_count,
            "watchlist_form": watchlist_form,
    }) 
    

@login_required(login_url='/login')
def createListing(request):
    watchlist_count = Watchlist.objects.filter(watched_by=request.user).count()
    if request.method == "POST":
        # Get Form
        form = ListingForm(request.POST)
        
        # Validate Form
        if form.is_valid():
            
            form = form.cleaned_data
            new_listing = Listing(title=form['title'],
                                description=form['description'],
                                price=form["price"],
                                category=form["category"],
                                photo_url=form['photo_url'],
                                lister=request.user)
            new_listing.save()

            return HttpResponseRedirect(reverse('index'))
        
        else:
            return render(request, "auctions/create_listing.html", {
                'form': form,
                'error': "One of the fields are invalid.",
                'watchlist_count': watchlist_count
            })
        
    else:
        return render(request, "auctions/create_listing.html", {
            'form': ListingForm,
            "watchlist_count": watchlist_count,
        })


@login_required(login_url="/login")
def closeListing(request, listing_id):
    # Close Listing if the user is the lister
    if request.method == "GET":
        try:
            current_listing = Listing.objects.get(pk=listing_id)
            logging.info("Checking for listing")
        except Listing.DoesNotExist:
            return HttpResponseRedirect('')
        
        if current_listing.lister != request.user:
            return HttpResponseRedirect('')
        
        else:
            
            current_listing.active = False
            current_listing.save()
            
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
    else:
        listings = {}

    return render(request, "auctions/watchlist.html", {
        "watchlist": listings,
        "watchlist_count": len(listings),
    })
    

@login_required(login_url="/login")
def toggleWatchlist(request):

    if request.method == "POST":

        form = WatchlistForm(request.POST)

        if form.is_valid():
            form = form.cleaned_data

            user = request.user

            listing = Listing.objects.get(id=form["listing_id"])

            # If the item is not in the database as a watched item by the user, create an entry
            try:
                is_watching = Watchlist.objects.get(listing=listing, watched_by=user)
            except Watchlist.DoesNotExist:
                is_watching = False

            if is_watching:
                is_watching.delete()
            else:
                watchlist_listing = Watchlist(listing=listing, watched_by=user)
                watchlist_listing.save()

            return redirect(f"/listings/{form['listing_id']}")

    else:
        return render(request, "auctions/error.html")
        

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

@login_required(login_url='/login')
def createComment(request):
    form = CommentForm(request.POST)
    logging.info(form)

    if form.is_valid():
    
        form = form.cleaned_data

        listing_id = form['listing_id']
        new_comment = Comment(
                       comment=form['comment'],
                       commenter= request.user,
                       comment_for = Listing.objects.get(pk=listing_id),
        )
        new_comment.save()

        return redirect(f"/listings/{listing_id}")
    