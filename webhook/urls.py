# webhook/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from subscriptions.views import WebhookIngestionView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
router = DefaultRouter()
# router.register(r'subscriptions', SubscriptionViewSet)
from subscriptions.views import DeliveryStatusView, SubscriptionDeliveryHistoryView

from subscriptions import urls as subscription_urls

urlpatterns = [
    path('api/', include(subscription_urls)),
    path('ingest/<str:subscription_id>/', WebhookIngestionView.as_view(), name='ingest_webhook'),
    path('api/deliveries/<str:webhook_identifier>/', DeliveryStatusView.as_view()),
    path('api/subscriptions/<str:identifier>/logs/', SubscriptionDeliveryHistoryView.as_view()),
]
