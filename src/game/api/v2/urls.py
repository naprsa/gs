from django.urls import path


from . import api

app_name = "game"

urlpatterns = [
    path("demo/", api.DeckListDemoApiView.as_view()),
    path(
        "deck/detail/<uuid:uid>/",
        api.UserDeckViewSet.as_view({"get": "deck_detail"}),
        name="deck_detail",
    ),
]
