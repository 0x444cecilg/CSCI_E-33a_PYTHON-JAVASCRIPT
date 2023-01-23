from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

def index(request):
    """Returns all active listings stored on the DB"""
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })

def login_view(request):
    if request.method == "POST":

        # Attempt and sign user in
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


@login_required
def create_listing(request):
    """Allows users to add new listing through a form."""
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        form = ListingForm(request.POST, request.FILES)
        # Verify if the form is filled out correctly, add listing to DB
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })

@login_required
def show_listing(request, listing_id):
    """Detailed page of a single auction."""
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        # verifies if the item is already on the users watchlist
        if request.POST.get("button") == "Watchlist": 
            if not user.watchlist.filter(listing= listing):
                watchlist = Watchlist()
                watchlist.user = user
                watchlist.listing = listing
                watchlist.save()
            else:
                user.watchlist.filter(listing=listing).delete()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        # user who created auction can close auction
        if not listing.closed:
            if request.POST.get("button") == "Close": 
                listing.closed = True
                listing.save()
            else:
                price = float(request.POST["price"])
                bids = listing.bids.all()
                # only users without item can place bid, bid must be greater than current price
                if user.username != listing.owner.username: 
                    if price <= listing.price:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "form": BidForm(),
                            "message": "Error! Invalid bid amount! Bid made is equal or less than the actual price. Please Try again."
                        })
                    form = BidForm(request.POST)
                    if form.is_valid():
                        bid = form.save(commit=False)
                        bid.user = user
                        bid.save()
                        listing.bids.add(bid)
                        listing.price = price
                        listing.save()
                    else:
                        return render(request, 'auctions/listing.html', {
                            "form": form
                        })
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": BidForm(),
            "message": ""
        })


@login_required
def watchlist(request):
    """Returns all auctions that are on user's watchlist."""
    user = User.objects.get(username=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all()
    })

def comment(request, listing_id):
    """Handles posting comments on auctions."""
    user = User.objects.get(username=request.user)
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        #Saves the comment on the DB
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.save()
            listing.comments.add(comment)
            listing.save()

            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        else:
            return render(request, "auctions/comment.html", {
                "form": form,
                "listing_id": listing.id,
            })
    else:
        return render(request, "auctions/comment.html", {
            "form": CommentForm(),
            "listing_id": listing.id
        })

@login_required
def categories(request):
    """Returns a list of categories"""
    return render(request, 'auctions/categories.html', {
        "categories": CATEGORIES,
    })

@login_required
def show_category_listings(request, category):
    """Returns a detailed view of all listings in a specific category"""
    listings = Listing.objects.filter(category__in = category[0])
    cat = dict(CATEGORIES)
    return render(request, 'auctions/specific.html', {
        "listings": listings,
        "category": cat[category]
    })
