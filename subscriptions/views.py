# subscriptions/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subscription
from .tasks import process_webhook_event
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse

class WebhookIngestionView(APIView):
    def post(self, request, subscription_id):
        # Get subscription details
        try:
            subscription = Subscription.objects.get(identifier=subscription_id)
        except Subscription.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)

        # Queue the webhook for asynchronous processing
        process_webhook_event.delay(subscription.id, request.data)
        return Response({"message": "Webhook ingestion successful"}, status=status.HTTP_202_ACCEPTED)



from rest_framework import viewsets
from .models import Subscription
from .serializers import SubscriptionSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionListCreateView(APIView):
    def get(self, request):  # List all subscriptions
        subscriptions = Subscription.objects.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def post(self, request):  # Create a new subscription
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionDetailView(APIView):
    def get(self, request, subscription_id):  # Get by ID
        try:
            subscription = Subscription.objects.get(identifier=subscription_id)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def put(self, request, subscription_id):  # Update
        try:
            subscription = Subscription.objects.get(identifier=subscription_id)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subscription_id):  # Delete
        try:
            subscription = Subscription.objects.get(identifier=subscription_id)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DeliveryLog
from .serializers import DeliveryLogSerializer

class DeliveryStatusView(APIView):
    def get(self, request, webhook_identifier):
        logs = DeliveryLog.objects.filter(webhook_identifier=webhook_identifier).order_by('-timestamp')
        if not logs.exists():
            return Response({"detail": "No logs found for the given webhook_identifier"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryLogSerializer(logs, many=True)
        return Response(serializer.data)


class SubscriptionDeliveryHistoryView(APIView):
    def get(self, request, identifier):
        logs = DeliveryLog.objects.filter(subscription__identifier=identifier).order_by('-timestamp')[:20]
        if not logs.exists():
            return Response({"detail": "No logs found for this subscription"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryLogSerializer(logs, many=True)
        return Response(serializer.data)
