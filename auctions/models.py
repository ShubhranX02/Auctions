from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.TextField(max_length=64)
    description = models.TextField(max_length=1024)
    image_url = models.URLField()
    category = models.TextField(max_length=4)
    
    auction_ended = models.BooleanField()

    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    starting = models.IntegerField()

    def highest_bid(self):
        if len(self.bids.all()) == 0:
            return self.starting
        else:
            return max([x.amount for x in self.bids.all()])

    def highest_bid_plusone(self):
        if len(self.bids.all()) == 0:
            return self.starting
        else:
            return max([x.amount for x in self.bids.all()]) + 1

    def highest_bidder(self):
        bids = self.bids.all()
        max = 0
        highest = None
        
        for bid in bids:
            if bid.amount > max:
                max = bid.amount
                highest = bid

        if highest is not None:
            return highest.bidder
        else:
            return 0

    def __str__(self):
        return f"{self.id}: {self.title}"


class Comment(models.Model):
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=256)


class Bid(models.Model):
    amount = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"${self.amount} on {self.listing.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listings = models.ManyToManyField(Listing, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Watchlist"