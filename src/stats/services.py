from .models import DeckAccessLog, PromocodeUsageLog


def log_promocode_usage(user, user_ip, code):
    log = PromocodeUsageLog.objects.create(user=user, code=code, user_ip=user_ip)
    code.counter = int(code.counter) + 1
    code.save(update_fields=["counter"])
    return log


def log_deck_access(data):
    player = data["player"]
    deck = data["deck"]
    player_ip = data["player_ip"]

    log = DeckAccessLog.objects.create(
        player=player if not player.is_anonymous else None,
        deck=deck,
        player_ip=player_ip,
    )
    return log
