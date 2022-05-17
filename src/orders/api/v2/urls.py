from django.urls import path
from . import api


app_name = "orders"

urlpatterns = [
    path("purchase/apple/", api.TransactionCheckAPIView.as_view({"post": "apple"})),
    path("purchase/google/", api.TransactionCheckAPIView.as_view({"post": "google"})),
    path("purchase/promo/", api.TransactionCheckAPIView.as_view({"post": "promo"})),
]
