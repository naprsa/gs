from django.urls import path
from . import views


app_name = "office"

urlpatterns = [
    path("create_fb/", views.CreateFeedbackApiView.as_view()),
]
