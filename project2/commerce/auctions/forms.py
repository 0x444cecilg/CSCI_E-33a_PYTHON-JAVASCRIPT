from django.forms import ModelForm

from .models import *

class ListingForm(ModelForm):
  class Meta:
    model = Listing
    fields = ['item', 'price', 'description', 'category', 'image']


class BidForm(ModelForm):
  class Meta:
    model = Bid
    fields = ["price"]

class CommentForm(ModelForm):
  class Meta:
    model = Comment
    fields = ["title", "comment"]