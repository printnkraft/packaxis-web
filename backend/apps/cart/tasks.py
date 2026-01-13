from celery import shared_task

@shared_task
def send_abandoned_cart_email(basket_id: int):
    # Implement abandoned cart email logic
    return "queued"