import base64
import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game.api.v1.serializers import CardDetailSerializer, BoxDetailSerializer
from game.models import DeckShirt, DeckFace, Deck


class FaceStyleImageListSerializer(serializers.Serializer):
    def get_images(self, obj):
        data = base64.b64encode(obj.img.read())
        return data

    def to_representation(self, instance):
        data = {}
        for image in instance:
            fname = os.path.basename(image.img.name).split(".")[0].lower()
            data[fname] = self.get_images(image)
        return data


class DeckDemoDetailSerializer(serializers.ModelSerializer):
    """
    Detail deck serializer
    """

    ownerId = serializers.SlugRelatedField(
        source="user", slug_field="uid", read_only=True
    )
    name_en = serializers.CharField(source="title")
    name_ru = serializers.CharField(source="title_ru", allow_blank=True, required=False)
    congratulations_en = serializers.CharField(
        source="cong_text", required=False, allow_blank=True
    )
    congratulations_ru = serializers.CharField(
        source="cong_text_ru", required=False, allow_blank=True
    )
    isMirrorOn = serializers.BooleanField(source="mirror")
    changed = serializers.DateTimeField(source="updated")
    cards = CardDetailSerializer(read_only=True, many=True)
    shirtId = serializers.SlugRelatedField(
        source="shirt",
        slug_field="uid",
        queryset=DeckShirt.objects.all(),
    )
    faceId = serializers.SlugRelatedField(
        source="face",
        slug_field="uid",
        queryset=DeckFace.objects.all(),
    )
    box = BoxDetailSerializer()

    class Meta:
        model = Deck
        fields = [
            "uid",
            "ownerId",
            "name_en",
            "name_ru",
            "box",
            "congratulations_en",
            "congratulations_ru",
            "shirtId",
            "faceId",
            "cards",
            "pin",
            "changed",
            "isMirrorOn",
        ]

    def validate_pin(self, value):
        if len(str(value)) > 4:
            raise ValidationError("Pin length can not be larger 4 digits")
        if not str(value).isdigit():
            raise ValidationError("Pin must contain only digits")
        return value
