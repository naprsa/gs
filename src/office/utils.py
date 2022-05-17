import shortuuid


def generate_promocode():
    return shortuuid.uuid().upper()[:4]
