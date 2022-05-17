from zipfile import ZipFile

from users.models import User
from orders.models import Transaction
from .models import Card, Box, Deck, Image, DeckShirt, ImageCollection, DeckFace


def make_cards(deck):
    cards_set = Card.CARD_VALUES
    suits_set = Card.SUITS
    for suit in suits_set:
        for card in cards_set:
            img = Image.objects.create()
            deck.cards.create(
                deck=deck,
                suit=suit[0],
                value=card[0],
                image=img,
            )


def make_box(deck):
    box = Box()
    image = Image.objects.create()
    box.image = image
    box.save()
    deck.box = box
    deck.save(update_fields=["box"])


def make_shirt(deck):
    img = Image.objects.create()
    shirt = DeckShirt.objects.create(image=img)
    deck.shirt = shirt
    deck.save()


def make_face_style(deck):
    images = ImageCollection.objects.create()
    face = DeckFace.objects.create(images=images)
    deck.face = face
    deck.save()


def create_deck_by_ta(user: User, ta: Transaction, data: dict):
    deck = Deck.objects.create(user=user, transaction=ta)
    if data:
        title = data.get("name", "")
        cong_text = data.get("congratulations", "")
        face_uid = data.get("faceId", None)
        shirt_uid = data.get("shirtId", None)
        pin = data.get("pin", "")
        mirror = data.get("isMirrorOn", None)

        if face_uid and DeckFace.objects.filter(uid=face_uid).exists():
            face = DeckFace.objects.get(uid=face_uid)
            deck.face = face
        if shirt_uid and DeckShirt.objects.filter(uid=shirt_uid).exists():
            shirt = DeckShirt.objects.get(uid=shirt_uid)
            deck.shirt = shirt
        if mirror:
            deck.mirror = mirror.capitalize()

        deck.title = title
        deck.cong_text = cong_text
        deck.pin = pin
        deck.save()
    return deck
