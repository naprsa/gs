import safedelete.models
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from game.api.v1.permissions import IsOwner
from game.api.v1.serializers import DeckDetailSerializer, DeckHistorySerializer
from game.api.v2.sertializers import DeckDemoDetailSerializer
from game.models import Deck, DeckFace


class DeckListDemoApiView(generics.ListAPIView):
    """No need auth for get demo game"""

    queryset = (
        Deck.objects.prefetch_related(
            "cards",
            "cards__image",
        )
        .select_related(
            "user",
            "shirt",
            "face",
            "transaction",
        )
        .filter(user__isnull=True, demo_mobile=True)
    )
    serializer_class = DeckDemoDetailSerializer
    permission_classes = [AllowAny]


class UserDeckViewSet(viewsets.GenericViewSet):
    """
    ACE = 0
    CARD_2 = 2
    CARD_3 = 3
    CARD_4 = 4
    CARD_5 = 5
    CARD_6 = 6
    CARD_7 = 7
    CARD_8 = 8
    CARD_9 = 9
    CARD_10 = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    *
    SPADES = 1
    DIAMONDS = 2
    CLUBS = 3
    HEARTS = 4

    ### ERRORS:
        PIN_ERROR: Pin invalid or missing
        IMAGE_NOT_EXISTS: Image does not exists
        OWNER_ERROR: Deck doesn't belong to user
    """

    queryset = (
        Deck.objects.prefetch_related("cards", "cards__image")
        .select_related(
            "user",
            "shirt",
            "face",
            "transaction",
        )
        .filter()
    )
    serializer_class = DeckDetailSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "uid"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "deck_detail":
            self.permission_classes = [
                AllowAny,
            ]
        elif self.action == "deck_update":
            self.permission_classes = [IsAuthenticated, IsOwner]
        return super().get_permissions()

    def user_decks(self, request):
        serializer = DeckDetailSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def deck_detail(self, request, uid=None):
        deck = generics.get_object_or_404(self.queryset, uid=uid)
        if deck.is_demo:
            serializer = DeckDemoDetailSerializer(deck)
        else:
            serializer = DeckDetailSerializer(deck)

        if deck.user != request.user and not deck.is_demo:
            pin = request.GET.get("pin")
            if not deck.check_pin(pin):
                raise ValidationError({"pin": ["Invalid pin"]}, code="PIN_ACCESS_ERROR")

        return Response(serializer.data)

    def deck_update(self, request, *args, uid=None, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def deck_delete(self, request, uid):
        deck = generics.get_object_or_404(self.get_queryset(), uid=uid)
        deck.delete(force_policy=safedelete.models.HARD_DELETE)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def decks_history(self, request, *args, **kwargs):
        user = request.user
        all_decks = Deck.all_objects.filter(user=user)
        serializer = DeckHistorySerializer(all_decks, many=True)
        return Response(serializer.data)


#
# class FaceDetailApiView(generics.RetrieveAPIView):
#     queryset = DeckFace.objects.prefetch_related("images__images").filter()
#     permission_classes = (AllowAny,)
#     serializer_class = FaceStyleImageListSerializer
#     lookup_field = "uid"
#
#     def get_object(self):
#         obj = super(FaceDetailApiView, self).get_object()
#         images = obj.images.get_collection_qs()
#         return images
#
#     def get(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
