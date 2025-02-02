from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from profiles.forms import CustomUserEditForm, CustomUserCreationFormForOrder
from django.urls import reverse
from .forms import OrderStep2Forms, OrderStep3Forms, OrderStep4Forms, OrderPaymentForm
from .services import get_cart_data, calculate_total_price, ServiceForPayment
from .models import OrderModel

# Create your views here.

class BaseOrderView(TemplateView):

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        user = request.user
        context["user"] = user
        return context


class OrderStepOneView(BaseOrderView):
    """"View for check user data and register or login (if not authenticated), then redirect to step2"""

    template_name = 'orders/order_detail.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context.get('user')
        phone_number = user.phone_number if user.is_authenticated else ''
        form = CustomUserEditForm(initial={'phone_number': phone_number})
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context.get('user')
        if not user.is_authenticated:
            post_data = request.POST.copy()
            post_data['password1'] = request.POST['password']
            post_data['password2'] = request.POST['password_reply']
            form = CustomUserCreationFormForOrder(post_data)
            if form.is_valid():
                form.save(request=request)
                return redirect(reverse('orders:orders_step2'))

            context['form'] = form
            return self.render_to_response(context)

        return redirect(reverse('orders:orders_step2'))


class OrderStepTwoView(BaseOrderView):
    """View for check type delivery, city, address and add in session (step 2), then redirect to step3"""

    template_name = 'orders/order_detail_2.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        form = OrderStep2Forms()
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        form = OrderStep2Forms(request.POST)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            request.session['order'] = {
                'delivery': delivery,
                'city': city,
                'address': address
            }
            return redirect(reverse('orders:orders_step3'))

        context['form'] = form
        return self.render_to_response(context)


class OrderStepThreeView(BaseOrderView):
    """view for check type pay and add in session (step 3), then redirect step4"""
    template_name = "orders/order_detail_3.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        form = OrderStep3Forms()
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        form = OrderStep3Forms(request.POST)
        if form.is_valid():
            order = request.session.get('order', {})
            order['pay'] = form.cleaned_data['pay']
            request.session['order'] = order
            return redirect(reverse('orders:orders_step4'))

        context['form'] = form
        return self.render_to_response(context)


class OrderStepFourView(BaseOrderView):
    """view for check all data, save order model and redirect to payment"""
    template_name = 'orders/order_detail_4.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context['user']
        order = request.session.get('order', {})
        order['cart_data'] = get_cart_data(user=user)
        order['total_cost'] = calculate_total_price(data=order['cart_data'], order=order)
        order['cart_items'] = [item['pk'] for item in order['cart_data']]
        request.session['order'] = order
        context = {'order': order,}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context['user']
        order = request.session['order']
        form_data = order.copy()
        form_data['cart_items'] = order['cart_items']
        form_data['user'] = user
        form = OrderStep4Forms(data=form_data)
        if form.is_valid():
            if form.cleaned_data['existing_order']:
                return redirect(reverse('orders:payment'))

            order_instance = form.save(commit=False)
            order_instance.save()
            order_instance.cart_items.set(form_data['cart_items'])
            order['pk'] = str(order_instance.pk)
            request.session['order'] = order
            return redirect(reverse('orders:payment'))

        context['form'] = form
        return self.render_to_response(context)


class OrderPaymentView(BaseOrderView):
    """
    View that handles the payment process for an order.
    It retrieves order details from the session, processes a payment form submission,
    updates the order with the provided card number, and initiates an asynchronous payment
    processing task using Celery. After initiating the task, it redirects the user to a payment progress page.
    """
    template_name = 'orders/payment.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        order = request.session.get('order')
        context['pay'] = order['pay']
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        order = request.session['order']
        order['card_number'] = request.POST.get('numero1')
        order['user'] = context['user']
        form = OrderPaymentForm(data=order)
        form.order_pk = order['pk']
        if form.is_valid():
            order_instance = form.save()
            payment = ServiceForPayment(
                order_pk=order['pk'],
                card_number=order['card_number'],
                total_cost=order['total_cost'],
                request=request
            )
            payment_id = payment.add_payment()
            order_instance.payment_id = payment_id
            order_instance.save()
            del order['user']
            order['payment_id'] = payment_id
            request.session.update({'order': order})
            return redirect(reverse('orders:payment_progress'))
        context['form'] = form
        return self.render_to_response(context)


class OrderPaymentProgressView(BaseOrderView):
    """
    View that handles the progress of a payment process.Check status task and return data to template.
    Refreshes the page until the task status is success.
    """
    template_name = 'orders/payment_progress.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context.get('user')
        user.cart.items.clear()  # отвязываем товары от корзины
        order = request.session['order']
        payment = ServiceForPayment(order_pk=order['pk'], card_number=order['card_number'],
                                    total_cost=order['total_cost'], request=request)

        payment_process_data = payment.get_payment_status(payment_id=order['payment_id'])
        if payment_process_data.status== 'SUCCESS':
            payment_data = payment_process_data.result
            context['data'] = payment_data
            order = OrderModel.objects.get(pk=order['pk'])
            if payment_data['order_data']['status_pay'] == 'not success':
                order.error_message = payment_data['order_data']['message']
            else:
                order.status = 'success'
                order.error_message = ''
            order.save()
            return self.render_to_response(context)
        return self.render_to_response(context)


class OrdersHistoryList(BaseOrderView):
    """
    View that displays the history of orders if user is authenticated.
    Else - redirect to login page
    """
    template_name = 'orders/orders_history_list.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context.get('user')
        if not user.is_authenticated:
            return redirect(reverse('profiles:login'))
        orders = OrderModel.objects.filter(user=user).order_by('-created_at')
        context.update({'orders': orders})
        return self.render_to_response(context)


class OrdersHistoryDetail(BaseOrderView):
    """
    View that displays detail information of specific order of user.
    If the order doesnt belong to the user - 403 error.
    """
    template_name = 'orders/orders_history_detail.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        user = context.get('user')
        if not user.is_authenticated:
            return redirect(reverse('profiles:login'))
        order_id = self.kwargs.get('id')
        order = get_object_or_404(OrderModel.objects.prefetch_related('cart_items__product_seller__product'), id=order_id)
        if order.user != user:
            raise PermissionDenied('У вас нет доступа к этому заказу.')
        context.update({'order': order, 'cart_items': order.cart_items.all()})
        return self.render_to_response(context)
    
        