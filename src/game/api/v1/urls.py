from django.urls import path


from . import api

app_name = "game"

urlpatterns = [
    path("score/create/", api.GameScoreApi.as_view()),
    path("deck/log/", api.GameLogApi.as_view()),
    path("user/", api.UserDeckViewSet.as_view({"get": "user_decks"})),
    path("demo/", api.DeckListDemoApiView.as_view()),
    path("demo/translations/", api.DemoDeckTranslationsApiView.as_view()),
    path(
        "purchased/",
        api.UserDeckViewSet.as_view({"get": "decks_history"}),
    ),
    path("shirts/", api.ShirtListApiView.as_view()),
    path("shirts/<uuid:uid>/", api.ShirtDetailApiView.as_view()),
    path("faces/", api.FaceListApiView.as_view()),
    path("faces/<uuid:uid>/data/", api.FaceDetailApiView.as_view()),
    path("web/<uuid:uid>/", api.WebPlayApiView.as_view()),
    path("web/check/<uuid:uid>/", api.WebPlayDeckCheckApiView.as_view()),
    path(
        "deck/detail/<uuid:uid>/",
        api.UserDeckViewSet.as_view({"get": "deck_detail"}),
        name="deck_detail",
    ),
    path(
        "deck/<uuid:uid>/",
        api.UserDeckViewSet.as_view({"delete": "deck_delete"}),
    ),
    path(
        "deck/<uuid:deck_uid>/box/upload/",
        api.BoxApiView.as_view({"put": "upload_image"}),
    ),
    path("deck/<uuid:deck_uid>/box/", api.BoxApiView.as_view({"get": "get_image"})),
    path(
        "deck/update/<uuid:uid>/",
        api.UserDeckViewSet.as_view({"put": "deck_update"}),
    ),
    path(
        "<uuid:deck_uid>/card/<int:suit>/<int:value>/",
        api.CardApiView.as_view({"get": "card_image"}),
    ),
    path(
        "upload/<uuid:deck_uid>/card/<int:suit>/<int:value>/",
        api.CardApiView.as_view({"post": "upload_card_image"}),
    ),
]
