from django import forms
from .models import OrderModel


class OrderStep2Forms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ['delivery', 'city', 'address']

    def clean(self):
        cleaned_data = super().clean()
        # print(cleaned_data, 'cleaned_data')
        return cleaned_data


class OrderStep3Forms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ['pay']

    def clean(self):
        cleaned_data = super().clean()
        # print(cleaned_data, 'cleaned_data')
        return cleaned_data