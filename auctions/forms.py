from decimal import Decimal
from django import forms

class BidForm(forms.Form):
    bid = forms.DecimalField(required=True, max_digits=9, decimal_places=2)