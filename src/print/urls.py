from django.urls import path
from .views import get_pdf


app_name = "print"

urlpatterns = [
    path("pdf/<uuid:deck_uid>/", get_pdf, name="get_pdf"),
]
