from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from game.api.v1.serializers import DeckDetailSerializer
from .serializers import (
    PurchaseDeckPromoSerializer,
    PurchaseDeckAppleSerializer,
    PurchaseDeckGoogleSerializer,
)


class TransactionCheckAPIView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "apple":
            return PurchaseDeckAppleSerializer
        if self.action == "google":
            return PurchaseDeckAppleSerializer
        if self.action == "promo":
            return PurchaseDeckPromoSerializer

    def promo(self, request):
        serializer = PurchaseDeckPromoSerializer(
            data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            deck = serializer.save()
            if isinstance(deck, str):
                data = {"promoProduct": deck}
            else:
                serializer = DeckDetailSerializer(deck)
                data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)

    def google(self, request):
        serializer = PurchaseDeckGoogleSerializer(
            data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            deck = serializer.save()
            serializer = DeckDetailSerializer(deck)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response()

    def apple(self, request):
        serializer = PurchaseDeckAppleSerializer(
            data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            deck = serializer.save()
            serializer = DeckDetailSerializer(deck)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
