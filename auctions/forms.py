from email.mime import audio
from django import forms
from .listing_categories import LISTING_CATEGORIES

class BidForm(forms.Form):
    bid = forms.DecimalField(required=True, max_digits=9, decimal_places=2)
    
class ListingForm(forms.Form):
    title = forms.CharField(
                            required=True, 
                            max_length=30, 
                            min_length=3,
                            label='',
                            widget= forms.TextInput(attrs={
                                'placeholder': 'Title',
                                'autofocus': "true",
                            }))
    
    description = forms.CharField(
                        max_length=500,
                        required=False,
                        label='',
                        widget=forms.Textarea(attrs= {
                            'placeholder': 'Description',
                        }))
    
    price = forms.DecimalField(initial=10,
                               decimal_places=2,
                               max_digits=10,
                               label='Initial Price',
                               required=True)
    
    category = forms.ChoiceField(choices=LISTING_CATEGORIES, initial='None')
    
    photo_url = forms.URLField(label='',
                               required=False,
                               max_length=160,
                               widget=forms.URLInput(attrs={
                                   'placeholder': "Photo URL (Optional)"
                               }))


class CommentForm(forms.Form):
    comment = forms.CharField(required=True,
                              max_length=300,
                              min_length=5,
                              widget=forms.TextInput(attrs={
                                'placeholder': 'Comment',
                              }))
    listing_id = forms.CharField(widget=forms.HiddenInput)


class WatchlistForm(forms.Form):
    listing_id = forms.CharField(widget=forms.HiddenInput)