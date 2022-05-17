from celery.app import shared_task
from core.celery import app
from icecream import ic
from time import sleep
from game.models import Deck
from .service import LayoutGenerator
from .models import PrintLayout


@app.task
def generate_layout(deck_uid):
    layout = None
    try:
        deck = Deck.objects.get(uid=deck_uid)
        layout = LayoutGenerator(deck)
    except Exception as e:
        status = str(e)
        return e
    path_to_file = layout.create_pdf()
    layout = PrintLayout.objects.get(deck=deck)
    layout.file = str(path_to_file)
    layout.save()
    return "done"
