import datetime
import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4

from safedelete.models import SafeDeleteModel

from core.utils import SingletonModel
from .utils import user_deck_path, make_img_hash
from icecream import ic


class ImageCollection(models.Model):
    def get_images_json(self):
        images = self.images.filter()
        return images

    def get_collection_qs(self):
        return self.images.filter()

    def get_collection_json(self):
        from .api.v1.serializers import ImageSerializer

        qs = self.get_collection_qs()
        serializer = ImageSerializer(qs, many=True)
        return serializer.data

    def get_value_img(self, value):
        qs = self.get_collection_qs()
        for img in qs:
            fname = os.path.basename(img.img.name).split(".")[0].lower()
            if value == 0:
                value = "a"
            elif value == 11:
                value = "j"
            elif value == 12:
                value = "q"
            elif value == 13:
                value = "k"

            if fname == str(value).lower():
                return img.img.path

    def get_suit_img(self, suit):
        suits = Card.SUITS
        for s in suits:
            if s[0] == suit:
                return self.get_value_img(s[1])

    def __str__(self):
        if hasattr(self, "model"):
            return self.model.title
        else:
            return super().__str__()


class Image(models.Model):
    """Model definition for Image."""

    img = models.ImageField(_("Image"), upload_to=user_deck_path, null=True)
    md5 = models.CharField(max_length=150, editable=False)
    collection = models.ForeignKey(
        ImageCollection,
        related_name="images",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta definition for Image."""

        verbose_name = "Image"
        verbose_name_plural = "Images"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.img:
            self.md5 = make_img_hash(self.img.path)
            super().save(update_fields=["md5"])

    @property
    def size(self):
        if self.img:
            size = self.img.size
        else:
            size = 0
        return size

    @property
    def get_deck(self):
        card = None
        if hasattr(self, "box"):
            deck = self.box.get_deck()
        elif hasattr(self, "card"):
            deck = self.card.get_deck()
            card = self.card
        elif hasattr(self, "images"):
            deck = "face"
        elif hasattr(self, "shirt"):
            deck = "shirt"
        else:
            deck = None
        return deck, card


class DeckShirt(models.Model):
    """Model definition for DeckShirt."""

    uid = models.UUIDField(_("Shirt uid"), default=uuid4)
    title = models.TextField("Title", blank=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    updated = models.DateTimeField("Last update", auto_now=True)
    image = models.ForeignKey(
        Image,
        verbose_name=_("Shirt image"),
        related_name="shirt",
        on_delete=models.CASCADE,
    )
    border_color = models.CharField(
        "Border color", blank=True, default="0D5822", max_length=10
    )

    class Meta:
        verbose_name = "Deck shirt"
        verbose_name_plural = "Deck shirts"

    def __str__(self):
        return self.title if self.title else super().__str__()


class DeckFace(models.Model):
    """Model definition for DeckFace."""

    uid = models.UUIDField(_("Face uid"), default=uuid4)
    title = models.TextField("Title", blank=True)
    images = models.OneToOneField(
        ImageCollection,
        verbose_name=_("Face images collection"),
        related_name="model",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField("Created", auto_now_add=True)
    updated = models.DateTimeField("Last update", auto_now=True)
    json_settings = models.JSONField("Json settings", blank=True, default=dict)
    md5 = models.CharField(max_length=150, editable=False, blank=True, default="")

    class Meta:
        """Meta definition for DeckSkin."""

        verbose_name = "Deck face style"
        verbose_name_plural = "Deck face styles"

    #
    def __str__(self):
        return self.title if self.title else super().__str__()


class DeckFacesJsonSchema(SingletonModel):
    json = models.JSONField("JSON Validation schema")


class Box(models.Model):
    """
    Box for card deck
    """

    created = models.DateTimeField(_("Created"), auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True, auto_now_add=False)
    image = models.OneToOneField(
        Image, verbose_name=_("Image"), on_delete=models.CASCADE, null=True
    )

    def get_deck(self):
        return self.deck


class Deck(SafeDeleteModel):
    """
    Deck of game model
    """

    uid = models.UUIDField(_("Deck UUID"), default=uuid4)
    title = models.CharField(_("Deck title"), blank=True, default="", max_length=150)
    cong_text = models.TextField(
        _("Congratulation text"), max_length=1000, blank=True, default=""
    )
    shirt = models.ForeignKey(
        DeckShirt,
        verbose_name=_("Shirt"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    face = models.ForeignKey(
        DeckFace,
        verbose_name=_("Face"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded = models.DateTimeField(
        _("Deck uploaded"), auto_now=False, auto_now_add=True
    )
    updated = models.DateTimeField(_("Deck updated"), auto_now=True, auto_now_add=False)
    pin = models.CharField(_("Deck PIN"), null=True, blank=True, max_length=4)
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
        related_name="decks",
        null=True,
        blank=True,
    )
    box = models.OneToOneField(
        Box,
        verbose_name=_("Deck box"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    transaction = models.OneToOneField(
        "orders.Transaction",
        verbose_name=_("Transaction"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    active = models.BooleanField(_("Active"), default=True)
    expires = models.DateTimeField("Date expire")
    mirror = models.BooleanField("Mirror ON", default=True, null=True)
    demo_mobile = models.BooleanField("For mobile apps", default=False)

    class Meta:
        verbose_name = _("Deck")
        verbose_name_plural = _("Decks")

    def __str__(self):
        return self.title if self.title else super().__str__()

    def save(self, **kwargs):
        if not self.pk:
            self.expires = timezone.now() + datetime.timedelta(days=365)
        return super(Deck, self).save(**kwargs)

    def get_owner(self):
        return self.user

    @property
    def is_demo(self):
        return True if not self.user else False

    def get_all_images(self):
        imgs = [self.face.images, self.shirt.image, self.box.image]
        for card in self.cards.all():
            imgs.append(card.image)
        return imgs

    def check_pin(self, pin):
        if self.is_demo:
            return True
        return self.pin == pin


class DeckTranslate(models.Model):
    deck = models.OneToOneField(
        Deck, related_name="translate", on_delete=models.CASCADE, null=True
    )
    title = models.CharField(_("Deck title"), blank=True, default="", max_length=150)
    cong_text = models.TextField(
        _("Congratulation text"), max_length=1000, blank=True, default=""
    )
    translate_prefix = models.CharField(
        _("Translate prefix(ru, en, de.."), max_length=3, default="ru"
    )
    date_updated = models.DateTimeField(_("Date updated"), auto_now=True)

    class Meta:
        verbose_name = _("Deck Translate")
        verbose_name_plural = _("Deck Translations")


class Card(models.Model):
    """
    Card of deck model
    """

    SPADES = 1
    DIAMONDS = 2
    CLUBS = 3
    HEARTS = 4

    SUITS = (
        (SPADES, _("Spades")),
        (DIAMONDS, _("Diamonds")),
        (CLUBS, _("Clubs")),
        (HEARTS, _("HEARTS")),
    )

    ACE = 0
    KING = 13
    QUEEN = 12
    JACK = 11
    CARD_2 = 2
    CARD_3 = 3
    CARD_4 = 4
    CARD_5 = 5
    CARD_6 = 6
    CARD_7 = 7
    CARD_8 = 8
    CARD_9 = 9
    CARD_10 = 10

    TOP_RANK_VALUES = [ACE, KING, QUEEN, JACK]

    CARD_VALUES = (
        (ACE, _("card_Ace")),
        (KING, _("card_King")),
        (QUEEN, _("card_Queen")),
        (JACK, _("card_Jack")),
        (CARD_2, "card_2"),
        (CARD_3, "card_3"),
        (CARD_4, "card_4"),
        (CARD_5, "card_5"),
        (CARD_6, "card_6"),
        (CARD_7, "card_7"),
        (CARD_8, "card_8"),
        (CARD_9, "card_9"),
        (CARD_10, "card_10"),
    )
    uid = models.UUIDField(_("Card UUID"), default=uuid4)
    deck = models.ForeignKey(
        Deck, verbose_name=_("Deck"), on_delete=models.CASCADE, related_name="cards"
    )
    image = models.OneToOneField(
        Image, verbose_name=_("Image"), on_delete=models.CASCADE, null=True
    )
    suit = models.PositiveSmallIntegerField(_("Card suit"), choices=SUITS)
    value = models.PositiveSmallIntegerField(_("Card value"), choices=CARD_VALUES)
    updated = models.DateTimeField(_("Updated"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self):
        return f"card_{self.suit}_{self.value}"

    def humanize_card(self):
        value = self.value
        suit = self.suit
        for v in self.CARD_VALUES:
            if v[0] == value:
                value = v[1].replace("card_", "")
        for s in self.SUITS:
            if suit == s[0]:
                suit = s[1]
        card = f"{value} {suit}"
        return card

    def get_deck(self):
        return self.deck


class GameScore(models.Model):
    user = models.ForeignKey(
        "users.User",
        verbose_name="Player",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="played_games",
    )
    deck = models.ForeignKey(
        "game.Deck",
        verbose_name="played with deck",
        on_delete=models.CASCADE,
        related_name="games",
    )
    score = models.PositiveSmallIntegerField("Game score")
    time = models.DurationField("Played time")
    won = models.BooleanField("Won the game", default=False)
    created = models.DateTimeField("Score created", auto_now_add=True)
    ip = models.CharField("IP of player", max_length=50)

    class Meta:
        verbose_name = "Game score"
        verbose_name_plural = "Game scores"

    def __str__(self):
        return f"{self.deck}: {self.score}"
