import mimetypes

from django.http import StreamingHttpResponse
from icecream import ic
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import safedelete.models


from print.service import LayoutGenerator
from game.models import Deck, Image, DeckShirt, DeckFace, GameScore, Card
from stats.models import DeckAccessLog
from . import messages
from .permissions import IsOwner
from .serializers import (
    DeckDetailSerializer,
    ImageSerializer,
    DeckShirtListSerializer,
    DeckFaceListSerializer,
    FaceStyleImageListSerializer,
    GameScoreSerializer,
    CardDetailSerializer,
    DeckHistorySerializer,
    ImageDetailSerializer,
    DeckWebPlayCheckSerializer,
    DeckAccessLogSerializer,
    DeckTranslateSerializer,
)
from core.utils import get_client_ip
from stats.services import log_deck_access


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
    serializer_class = DeckDetailSerializer
    permission_classes = [AllowAny]


class DemoDeckTranslationsApiView(generics.ListAPIView):
    queryset = Deck.objects.select_related("translate").filter(
        user__isnull=True, demo_mobile=True
    )
    serializer_class = DeckTranslateSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = []
        for deck in qs:
            serializer = self.get_serializer(deck)
            print(serializer.data)
            data.append(serializer.data)
        return Response(data)


class WebPlayDeckCheckApiView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Deck.objects.all()
    serializer_class = DeckWebPlayCheckSerializer
    lookup_field = "uid"


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


class CardApiView(viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action == "card_image":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def card_image(self, request, deck_uid, suit, value):
        pin = request.GET.get("pin")
        deck = generics.get_object_or_404(Deck.objects.all(), uid=deck_uid)
        image = deck.cards.get(suit=suit, value=value).image
        if deck.user != request.user and not deck.is_demo:
            if not deck.check_pin(pin):
                raise ValidationError({"pin": ["Invalid pin"]}, code="PIN_ACCESS_ERROR")

        if image.img:
            filename = image.img
            size = filename.size
            content_type_file = mimetypes.guess_type(filename.path)[0]

            response = StreamingHttpResponse(
                open(image.img.path, "rb"), content_type=content_type_file
            )
            response["Content-Disposition"] = "attachment; filename=%s" % str(filename)
            response["Content-Length"] = size
            return response
        else:
            return Response(
                messages.IMAGE_ERROR,
                status=status.HTTP_204_NO_CONTENT,
            )

    def upload_card_image(self, request, deck_uid, suit, value):
        deck = generics.get_object_or_404(Deck.objects.filter(), uid=deck_uid)
        if deck.user != request.user:
            raise ValidationError(
                {"user": ["Current user not owner of selected deck"]},
                code="ACCESS_DENIED",
            )
        try:
            file = request.data["file"]
        except KeyError:
            raise ParseError("Request has no resource file attached")
        card = deck.cards.get(suit=suit, value=value)
        image = card.image
        image.img = file
        image.save()
        card.save()
        serializer = CardDetailSerializer(card, read_only=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WebPlayApiView(generics.RetrieveAPIView):
    queryset = (
        Deck.objects.prefetch_related("cards", "cards__image")
        .select_related("face", "shirt")
        .filter()
    )
    lookup_field = "uid"
    # serializer_class = DeckWebPlaySerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        deck = self.get_object()
        pin = request.GET.get("pin")
        if not deck.check_pin(pin):
            raise ValidationError({"pin": ["Invalid pin"]}, code="PIN_ACCESS_ERROR")

        log = {
            "deck": deck,
            "player": request.user,
            "player_ip": get_client_ip(request),
        }
        log_deck_access(log)

        generator = LayoutGenerator(deck)
        data = generator.make_web_play_cards()
        return Response(data)


class ShirtListApiView(generics.ListAPIView):
    queryset = DeckShirt.objects.filter().order_by("pk")
    permission_classes = (AllowAny,)
    serializer_class = DeckShirtListSerializer
    lookup_field = "uid"


class FaceListApiView(generics.ListAPIView):
    queryset = (
        DeckFace.objects.prefetch_related("images__images").filter().order_by("pk")
    )
    permission_classes = (AllowAny,)
    serializer_class = DeckFaceListSerializer


class ShirtDetailApiView(generics.RetrieveAPIView):
    queryset = DeckShirt.objects.filter()
    permission_classes = (AllowAny,)
    lookup_field = "uid"

    def get_object(self):
        obj = super(ShirtDetailApiView, self).get_object()
        obj = obj.image
        return obj

    def retrieve(self, request, *args, **kwargs):
        image = self.get_object()
        filename = image.img
        size = filename.size

        content_type_file = mimetypes.guess_type(filename.path)[0]

        response = StreamingHttpResponse(
            open(image.img.path, "rb"), content_type=content_type_file
        )
        response["Content-Disposition"] = "attachment; filename=%s" % str(filename)
        response["Content-Length"] = size
        return response


class BoxApiView(viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    http_method_names = ["get", "put"]

    def get_image(self, request, deck_uid):
        deck = generics.get_object_or_404(Deck.objects.all(), uid=deck_uid)
        image = deck.box.image

        if image.img:
            filename = image.img
            size = filename.size
            content_type_file = mimetypes.guess_type(filename.path)[0]

            response = StreamingHttpResponse(
                open(image.img.path, "rb"), content_type=content_type_file
            )
            response["Content-Disposition"] = "attachment; filename=%s" % str(filename)
            response["Content-Length"] = size
            return response
        else:
            return Response(
                messages.IMAGE_ERROR,
                status=status.HTTP_204_NO_CONTENT,
            )

    def upload_image(self, request, deck_uid):
        deck = generics.get_object_or_404(Deck.objects.filter(), uid=deck_uid)
        if deck.user != request.user:
            raise ValidationError(
                {"user": ["Current user not owner of selected deck"]},
                code="ACCESS_DENIED",
            )
        try:
            file = request.data["file"]
        except KeyError:
            raise ParseError("Request has no resource file attached")
        image = deck.box.image
        image.img = file
        image.save()
        deck.box.save()
        deck.save()
        serializer = ImageDetailSerializer(image, read_only=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FaceDetailApiView(generics.RetrieveAPIView):
    queryset = DeckFace.objects.prefetch_related("images__images").filter()
    permission_classes = (AllowAny,)
    serializer_class = FaceStyleImageListSerializer
    lookup_field = "uid"

    def get_object(self):
        obj = super(FaceDetailApiView, self).get_object()
        images = obj.images.get_collection_qs()
        return images

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GameScoreApi(CreateAPIView):
    queryset = GameScore.objects.all()
    serializer_class = GameScoreSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        ip = get_client_ip(self.request)
        serializer.save(user=user, ip=ip)


class GameLogApi(CreateAPIView):
    queryset = DeckAccessLog.objects.all()
    serializer_class = DeckAccessLogSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        ip = get_client_ip(self.request)
        serializer.save(player=user, player_ip=ip)
