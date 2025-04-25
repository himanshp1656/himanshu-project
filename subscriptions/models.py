from django.db import models

class Subscription(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    target_url = models.URLField()
    secret_key = models.CharField(max_length=255, blank=True, null=True)  # Optional for signature verification

    def __str__(self):
        return self.identifier


# models.py
class DeliveryLog(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    webhook_identifier = models.CharField(max_length=255)  # you can generate a UUID for each webhook task
    target_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attempt_number = models.PositiveIntegerField()
    outcome = models.CharField(max_length=50)  # e.g., "Success", "Failed Attempt", "Failure"
    http_status = models.PositiveIntegerField(null=True, blank=True)
    error_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subscription.identifier} | Attempt {self.attempt_number} | {self.outcome}"
