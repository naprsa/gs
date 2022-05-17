import pathlib
import hashlib

from icecream import ic


def user_deck_path(instance, filename):
    deck, card = instance.get_deck
    if deck == "shirt":
        dir = "shirts"
        path = "/".join(["stuff", dir, filename])
    elif card:
        card_dir = ""
        for i in card.SUITS:
            if i[0] == card.suit:
                card_dir = f"{i[1].lower()}"

        if deck.is_demo:
            dir = f"demo/{deck.uid}/{card_dir}"
            path = "/".join(["decks", dir, filename])
        else:
            dir = f"{deck.user.uid}/{deck.uid}/{card_dir}"
            path = "/".join(["decks", dir, filename])
    else:
        dir = "unknown"
        path = "/".join([dir, filename])
    return path


def make_img_hash(img):
    img_hash = hashlib.md5(pathlib.Path(img).read_bytes()).hexdigest()
    return img_hash


def make_hash(obj):
    hashed = hashlib.md5(obj)
    return hashed.hexdigest()
