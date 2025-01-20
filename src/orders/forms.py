from django import forms
from django.core.exceptions import ValidationError

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


class OrderStep4Froms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ["delivery", "city", "address", "pay",'total_cost',]

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        delivery = cleaned_data.get('delivery')
        city = cleaned_data.get('city')
        address = cleaned_data.get('address')
        pay = cleaned_data.get('pay')
        total_cost = cleaned_data.get('total_cost')

        if OrderModel.objects.filter(
            user=user,
            delivery=delivery,
            city=city,
            address=address,
            pay=pay,
            total_cost=total_cost
        ).exists():
            raise ValidationError("Заказ с такими данными уже существует")

        return cleaned_data
