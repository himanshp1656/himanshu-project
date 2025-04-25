from django.urls import path
from .views import SubscriptionListCreateView , SubscriptionDetailView

urlpatterns = [
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription_create'),
    path('subscriptions/<str:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
]
