# subscriptions/tasks.py

from celery import shared_task
from .models import DeliveryLog, Subscription
import requests, time, uuid
from django.utils import timezone
from django.core.cache import cache

@shared_task(bind=True)
def process_webhook_event(self, subscription_id, payload):
    subscription_key = f"subscription_{subscription_id}"
    subscription = cache.get(subscription_key)
    if not subscription:
        # If subscription is not in cache, fetch it from the database
        try:
            print(f"Fetching subscription {subscription_id} from DB")
            subscription = Subscription.objects.get(id=subscription_id)
            # Cache the subscription details (target_url, secret) for 5 minutes
            cache.set(subscription_key, subscription, timeout=300)  # Cache for 5 minutes
        except Subscription.DoesNotExist:
            raise Exception(f"Subscription with id {subscription_id} does not exist.")
    else:
        print(f"Using cached subscription {subscription_id}")
    target_url = subscription.target_url
    retries = 5
    delay = 2  # Initial delay
    webhook_id = str(uuid.uuid4())  # Unique ID for this webhook task

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(target_url, json=payload, timeout=10)
            outcome = "Success" if response.status_code == 200 else "Failed Attempt"
            if outcome == "Success":
                DeliveryLog.objects.create(
                subscription=subscription,
                webhook_identifier=webhook_id,
                target_url=target_url,
                attempt_number=attempt,
                outcome=outcome,
                http_status=response.status_code,
            )
                return "Delivery successful"
            else:
                # If not success, raise exception to trigger retry
                raise Exception(f"Unexpected status code: {response.status_code}")
            # Log entry for this attempt
        except Exception as e:
            # Log failure or retry attempt
            outcome = "Failed Attempt" if attempt < retries else "Failure"
            DeliveryLog.objects.create(
                subscription=subscription,
                webhook_identifier=webhook_id,
                target_url=target_url,
                attempt_number=attempt,
                outcome=outcome,
                error_details=str(e),
            )

            if attempt < retries:
                time.sleep(delay)
                delay **= 2  # Exponential backoff
            else:
                return f"Failed after {retries} attempts: {str(e)}"



# tasks.py
from datetime import timedelta

@shared_task
def delete_old_delivery_logs():
    # cutoff = timezone.now() - timedelta(hours=72)
    cutoff = timezone.now() - timedelta(seconds=72)
    deleted_count, _ = DeliveryLog.objects.filter(timestamp__lt=cutoff).delete()
    return f"{deleted_count} logs deleted"
