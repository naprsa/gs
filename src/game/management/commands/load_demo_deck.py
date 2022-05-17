import os.path
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from icecream import ic
import zipfile

from game.models import Deck, DeckShirt, DeckFace


class Command(BaseCommand):
    help = "Load demo deck"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--file",
            default=False,
            required=True,
            help="full path to zip archive",
        )

    def handle(self, *args, **kwargs):
        shirts = DeckShirt.objects.all().values("pk", "title")
        faces = DeckFace.objects.all().values("pk", "title")
        file = kwargs["file"]
        if not os.path.isfile(file):
            raise FileNotFoundError("No such file")
        name = input("deck name: ")
        cong_text = input("Cong_text: ")
        print("choose shirt:")
        for i in shirts:
            print(f"{i['pk']} - {i['title']}")
        shirt_pk = input("shirt: ")
        print("choose face style:")
        for i in faces:
            print(f"{i['pk']} - {i['title']}")
        face_pk = input("face pk: ")

        deck = Deck.objects.create(
            title=name,
            cong_text=cong_text,
            face_id=face_pk,
            shirt_id=shirt_pk,
        )

        with zipfile.ZipFile(file, "r") as archive:

            path = os.path.join(settings.MEDIA_ROOT, "decks", "demo", str(deck.uid))
            archive.extractall(path)
            images = [
                file
                for file in archive.namelist()
                if not (file.startswith((".", "_", "__")) or file.endswith("/"))
            ]
            for image in images:
                suit, file = image.split("/")
                if suit == "spades":
                    suit = 1
                elif suit == "diamonds":
                    suit = 2
                elif suit == "clubs":
                    suit = 3
                elif suit == "hearts":
                    suit = 4
                value = file.split(".")[0].lower()
                if value == "a":
                    value = 0
                elif value == "j":
                    value = 11
                elif value == "q":
                    value = 12
                elif value == "k":
                    value = 13
                else:
                    value = int(value)

                card = deck.cards.get(suit=suit, value=value)
                card.image.img = f"decks/demo/{deck.uid}/{image}"
                card.image.save(update_fields=["img"])
                card.save()
