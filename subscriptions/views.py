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



from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import uuid

SUBSCRIPTIONS = {}
DELIVERY_LOGS = {}

def home(request):
    # HTML content as a string
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Service API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        h2 {
            color: #4CAF50;
        }
        .api-section {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .api-section ul {
            list-style-type: none;
            padding: 0;
        }
        .api-section li {
            padding: 8px 0;
            font-size: 16px;
        }
        .api-section li span {
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>

    <h1>Welcome to the Subscription Service API</h1>
    <p>Below are the available API endpoints:</p>

    <div class="api-section">
        <h2>1. `api/subscription`</h2>
        <ul>
            <li><span>GET</span>: Fetches a list of all subscriptions.</li>
            <li><span>POST</span>: Creates a new subscription.</li>
        </ul>
    </div>

    <div class="api-section">
        <h2>2. `api/subscription/&lt;identifier&gt;`</h2>
        <ul>
            <li><span>GET</span>: Fetches details for a specific subscription.</li>
            <li><span>PUT</span>: Updates the subscription with the given identifier.</li>
            <li><span>DELETE</span>: Deletes the subscription with the given identifier.</li>
        </ul>
    </div>

    <div class="api-section">
        <h2>3. `ingest/&lt;identifier&gt;`</h2>
        <ul>
            <li><span>POST</span>: Ingests data for the task identified by the given identifier.</li>
        </ul>
    </div>

    <div class="api-section">
        <h2>4. `api/subscription/&lt;identifier&gt;/logs`</h2>
        <ul>
            <li><span>GET</span>: Fetches the logs of tasks related to the subscription with the given identifier.</li>
        </ul>
    </div>

    <div class="api-section">
        <h2>5. `api/deliveries/&lt;uuid&gt;`</h2>
        <ul>
            <li><span>GET</span>: Fetches the history of a specific delivery task using the provided UUID.</li>
        </ul>
    </div>

</body>
</html>

    """
    
    # Replacing the placeholders with actual data
    html_content = html_content.replace("{% csrf_token %}", "")  # Replace CSRF token as it's only needed for POST requests, can be handled separately in a real case
    
    # Prepare subscriptions data for embedding in HTML
    subscriptions_html = ""
    for identifier, data in SUBSCRIPTIONS.items():
        subscriptions_html += f"""
        <tr>
            <td>{identifier}</td>
            <td>{data['details']}</td>
            <td>
                <a href="/ingest/{identifier}" class="btn">Ingest</a>
                <a href="/delete-subscription/{identifier}" class="btn">Delete</a>
                <button class="btn" onclick="fetchLogs('{identifier}')">View Logs</button>
            </td>
        </tr>
        """
    
    html_content = html_content.replace("{% for identifier, data in subscriptions.items %}", subscriptions_html)

    return HttpResponse(html_content)