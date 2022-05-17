import base64
import os

from django.core.exceptions import ValidationError
from rest_framework import serializers
from stats.models import DeckAccessLog
from game.models import (
    Deck,
    Card,
    Box,
    Image,
    DeckFace,
    DeckShirt,
    GameScore,
)


class DeckTranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = "__all__"

    def get_translations(self, obj):
        title_data = {"default": obj.title}
        cong_text = {"default": obj.cong_text}
        translate_updated = None
        if hasattr(obj, "translate"):
            title_data.update({obj.translate.translate_prefix: obj.translate.title})
            cong_text.update({obj.translate.translate_prefix: obj.translate.cong_text})
            translate_updated = obj.translate.date_updated
        data = {
            "title": title_data,
            "congratulation": cong_text,
            "translate_updated": translate_updated,
        }
        return data

    def to_representation(self, obj):
        return {str(obj.uid): self.get_translations(obj)}


class ImageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("md5", "size")


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ("image",)

    def get_image(self, obj):
        return obj.img.read()

    def to_representation(self, instance):
        if instance.collection:
            fname = os.path.basename(instance.img.name).split(".")[0].lower()
            return {fname: self.get_image(instance)}
        return super(ImageSerializer, self).to_representation(instance)


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


class DeckFaceListSerializer(serializers.ModelSerializer):
    settings = serializers.JSONField(source="json_settings")

    class Meta:
        model = DeckFace
        fields = ["uid", "title", "md5", "updated", "settings"]


class DeckShirtListSerializer(serializers.ModelSerializer):
    image = ImageDetailSerializer()
    borderColor = serializers.CharField(source="border_color")

    class Meta:
        model = DeckShirt
        fields = ["uid", "title", "image", "borderColor"]


class CardDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = [
            "suit",
            "value",
            "image",
            "updated",
        ]

    def get_image(self, obj):
        if obj.image.size != 0:
            image = ImageDetailSerializer(obj.image)
            return image.data
        else:
            pass


class BoxDetailSerializer(serializers.ModelSerializer):
    image = ImageDetailSerializer(read_only=True)

    class Meta:
        model = Box
        exclude = ["id", "created", "updated"]


class DeckHistorySerializer(serializers.ModelSerializer):
    """
    History of decks serializer
    """

    name = serializers.CharField(source="title")

    class Meta:
        model = Deck
        fields = [
            "uid",
            "name",
            "uploaded",
        ]


class DeckDetailSerializer(serializers.ModelSerializer):
    """
    Detail deck serializer
    """

    ownerId = serializers.SlugRelatedField(
        source="user", slug_field="uid", read_only=True
    )
    name = serializers.CharField(source="title")
    congratulations = serializers.CharField(
        source="cong_text", required=False, allow_blank=True
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
            "name",
            "box",
            "congratulations",
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


class GameScoreSerializer(serializers.ModelSerializer):
    deck = serializers.SlugRelatedField(slug_field="uid", queryset=Deck.objects.all())

    class Meta:
        model = GameScore
        fields = ["score", "time", "deck", "won"]


class DeckAccessLogSerializer(serializers.ModelSerializer):
    deck = serializers.SlugRelatedField(slug_field="uid", queryset=Deck.objects.all())

    class Meta:
        model = DeckAccessLog
        fields = ["deck"]


class DeckWebPlayCheckSerializer(serializers.ModelSerializer):
    congratulations = serializers.CharField(
        source="cong_text", required=False, allow_blank=True
    )
    is_demo = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ["congratulations", "is_demo"]

    def is_demo(self, obj):
        if obj.user:
            return False
        else:
            return True
