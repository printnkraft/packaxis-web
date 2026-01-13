from celery import shared_task

@shared_task
def sync_inventory():
    # Implement external inventory sync logic here
    return "ok"