from celery import shared_task

from products.services.day_offer_service import DayOfferService


@shared_task
def update_random_product_task():
    DayOfferService.update_random_product()
