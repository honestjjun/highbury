from django import forms

from .models import UsePoint


class UsePointForm(forms.ModelForm):
    class Meta:
        model = UsePoint
        fields = ('category', 'product_category', 'product', 'user', 'use_point')
