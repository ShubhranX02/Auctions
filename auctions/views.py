from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Watchlist, Bid, Comment
import re

listing_categories = [
    ("1", "Electronics"),
    ("2", "Fashion"),
    ("3", "Food"),
    ("4", "Home"),
    ("5", "Toys"),
    ("6", "Miscellaneous")
]

class CreateListingForm(forms.Form):
    title = forms.CharField(max_length=64, label="Title", widget=forms.TextInput(attrs={'class': 'create-input'}))
    description = forms.CharField(widget=forms.Textarea, max_length=1024)
    image_url = forms.URLField()
    category = forms.ChoiceField(choices=listing_categories)
    
    starting_price = forms.IntegerField(min_value=1, label="Starting Price (In Dollars):")


def sign_in_check(func):

    def wrapper(request, **kwargs):
        if request.user.is_authenticated:
            return func(request, **kwargs)
        else:
            return HttpResponseRedirect(reverse("login"))

    return wrapper

@sign_in_check
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "watchlist": request.user.watchlist.all().first().listings.all()
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
            watchlist = Watchlist(user=user)
            watchlist.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@sign_in_check
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            starting_price = form.cleaned_data["starting_price"]
            lister = request.user
            auction_ended = False

            listing = Listing(title=title, description=description, image_url=image_url, category=category, starting=starting_price, lister=lister, auction_ended=auction_ended)
            listing.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": CreateListingForm()
        })

@sign_in_check
def watchlist(request):
    if request.method == "POST":
        pass

    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all().first().listings.all()
    })

@sign_in_check
def add_to_watchlist(request):
    if request.method == "POST":
        listing = Listing.objects.get(pk=request.POST["listing-id"])
        user = request.user
        watchlist = user.watchlist.all().first()
        if request.POST["fate"] == "add":
            watchlist.listings.add(listing)
            watchlist.save()
        else:
            watchlist.listings.remove(listing)
            watchlist.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@sign_in_check
def display(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=id)
        listing.auction_ended = True
        listing.save()

    listing = Listing.objects.get(pk=id)

    return render(request, "auctions/display.html", {
        "listing": listing,
        "current_price": listing.highest_bid(),
        "bids": len(listing.bids.all()),
        "watchlist": request.user.watchlist.all().first().listings.all(),
        "comments": listing.comments.all(),
    })



@sign_in_check
def categories(request):
    listings = Listing.objects.all()
    listing_per_category = dict.fromkeys([x[0] for x in listing_categories], 0)
    ac = {}

    for category in listing_per_category:
        for listing in listings:
            if listing.category == category:
                listing_per_category[category] += 1

    for category in listing_categories:
        ac[category[1]] = listing_per_category[category[0]]

    return render(request, "auctions/categories.html", {
        "categories": ac
    })  

@sign_in_check
def view_category(request, category):
    for i in listing_categories:
        if i[1] == category:
            category_num = i[0]

    return render(request, "auctions/view_category.html", {
        "listings": Listing.objects.filter(category=category_num),
        "category": category,
        "watchlist": request.user.watchlist.all().first().listings.all()
    })

@sign_in_check
def search(request):
    if request.method == "POST":
        search = request.POST["search"]
        
        listings = Listing.objects.all()
        filtered = []
        search_re = re.compile(search)

        for listing in listings:
            if search_re.search(listing.title.lower()) is not None:
                filtered.append(listing)

        return render(request, "auctions/search_results.html", {
            "listings": filtered,
            "watchlist": request.user.watchlist.all().first().listings.all(),
            "search": search
        })

@sign_in_check
def bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        amount = request.POST["bid"]

        bid = Bid(listing=listing, bidder=request.user, amount=amount)
        bid.save()

        return HttpResponseRedirect(reverse("display", args=[listing_id]))

@sign_in_check
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        comment_ = request.POST["comment"]

        comment = Comment(listing=listing, commentor=request.user, comment=comment_)
        comment.save()

        return HttpResponseRedirect(reverse("display", args=[listing_id]))