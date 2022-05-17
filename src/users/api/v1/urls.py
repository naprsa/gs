from django.urls import path


from . import api


app_name = "users"

urlpatterns = [
    path("profile/", api.UserApiView.as_view()),
]
