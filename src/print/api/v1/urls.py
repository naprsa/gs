from django.urls import path


from . import api

app_name = "print"

urlpatterns = [
    path("<uuid:deck_uid>/", api.GetPrintLayout.as_view()),
]
