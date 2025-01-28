from django import forms
from django.core.exceptions import ValidationError

from .models import OrderModel
from cart.models import CartItem


class OrderStep2Forms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ['delivery', 'city', 'address']


class OrderStep3Forms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ['pay']



class OrderStep4Forms(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ["user","delivery", "city", "address", "pay",'total_cost', 'cart_items']

    cart_items = forms.ModelMultipleChoiceField(
        queryset=CartItem.objects.all(),
        required=True
    )

    def clean(self):
        """The clean method validates form data and checks if an order with the same details
        (user, delivery, city, address, payment, total cost, and cart items) already exists.
        If a match is found, it sets the existing_order flag to True; otherwise, it remains False."""

        cleaned_data = super().clean()
        cleaned_data['existing_order'] = False
        cart_items = cleaned_data.get('cart_items')
        existing_orders = OrderModel.objects.filter(
            user=cleaned_data.get('user'),
            delivery=cleaned_data.get('delivery'),
            city=cleaned_data.get('city'),
            address=cleaned_data.get('address'),
            pay=cleaned_data.get('pay'),
            total_cost=cleaned_data.get('total_cost')
        )
        for existing_order in existing_orders:
            existing_cart_items = set(existing_order.cart_items.values_list('id', flat=True))
            new_cart_items = set(item.id for item in cart_items)

            if existing_cart_items == new_cart_items:
                cleaned_data['existing_order'] = True
                break
        else:
            cleaned_data['existing_order'] = False

        return cleaned_data

class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = '__all__'

    card_number = forms.CharField(max_length=9)

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if card_number:
            cleaned_number = card_number.replace(' ', '')
            if len(cleaned_number) != 8:
                raise forms.ValidationError('Invalid card number format')
            return cleaned_number

        raise forms.ValidationError('Required card number')

    def save(self):
        order = OrderModel.objects.filter(pk=self.order_pk).first()
        order.card_number = self.cleaned_data['card_number']
        order.save()
        return order