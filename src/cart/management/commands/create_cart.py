from uuid import uuid4
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

from cart.models import Cart


class Command(BaseCommand):
    """Creates user cart"""

    def handle(self, *args, **options):
        self.stdout.write('Creating cart')
        
        user = User.objects.first()
        if user.cart.name is not None:
            self.stdout.write(self.style.ERROR(f'Cart not created. User {user.email} already has cart'))
            return
        cart = Cart()
        if user:
            cart.user = user
        else:
            cart.session_id = str(uuid4())
        cart.save()

        self.stdout.write(self.style.SUCCESS(f'Created cart {cart.pk}!'))