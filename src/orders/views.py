from django.shortcuts import redirect
from django.views.generic import TemplateView
from products.models import Category
from profiles.forms import CustomUserEditForm, CustomUserCreationFormForOrder
from django.urls import reverse
from .forms import OrderStep2Forms, OrderStep3Forms, OrderStep4Forms, OrderPaymentForm
from .tasks import process_payment
from .services import get_cart_data, calculate_total_price, ServiceForPayment

# Create your views here.

class BaseOrderView(TemplateView):

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list = Category.objects.all()
        user = request.user
        context['category_list'] = category_list
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
        print(order)
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
            form.save()
            payment = ServiceForPayment(order_pk=order['pk'],card_number=order['card_number'],total_cost=order['total_cost'])
            result = payment.add_payment()
            del order['user']
            request.session['order'] = order
            request.session['task_id'] = result
            return redirect(reverse('orders:payment_progress'))
        context['form'] = form
        return self.render_to_response(context)


class OrderPaymentProgressView(BaseOrderView):
    """
    View that handles the progress of a payment process.Check status task and return data to template
    """
    template_name = 'orders/payment_progress.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request)
        order = request.session['order']
        payment = ServiceForPayment(order_pk=order['pk'], card_number=order['card_number'],
                                    total_cost=order['total_cost'])
        result = payment.get_payment_status()
        if result.get('result') == 'success':
            context['data'] = result
            print(result)
            return self.render_to_response(context)