import base64
import os
import sys
import time

from io import BytesIO
from PIL import Image, ImageDraw
from itertools import zip_longest
from django.conf import settings
from icecream import ic

from game.models import Deck

COLS = 5
ROWS = 4
DEFAULT_BACKGROUND_COLOR = "white"
BOX_BG_COLOR = (25, 117, 50)
CANVAS_SIZE = (3777, 5313)
PAGE_BORDER_PADDING = (136, 526)
CARD_SIZE = (679, 1048)
WEB_CARD_SIZE = (673, 888)
SHIRT_SIZE = (714, 1083)
CARD_INNER_PADDING = (41, 47)
CARD_IMAGE_SIZE = (575, 753)
CARD_IMAGE_MARGIN = (68, 151)
CARD_PADDING = (12, 12)
CARD_INNER_SIZE = (198, 314)
CARD_INNER_MARGIN = (
    (CARD_SIZE[0] - CARD_INNER_SIZE[0]) / 2,
    (CARD_SIZE[1] - CARD_INNER_SIZE[1]) / 2,
)
MARKER_PADDING = 35
SHIRT_MARKER_PADDING = 17
MARKER_INNER_OFFSET = 12
CARDS_COUNT = 52


class LayoutGenerator(object):
    """docstring for Collage"""

    def __init__(self, deck=None):
        super(LayoutGenerator, self).__init__()
        self.cols = COLS
        self.rows = ROWS
        self.card_size = CARD_SIZE
        self.page_border_padding = PAGE_BORDER_PADDING
        self.def_bg_color = DEFAULT_BACKGROUND_COLOR
        self.box_bg_color = BOX_BG_COLOR
        self.canvas_size = CANVAS_SIZE
        self.deck = deck
        self.pages = []

    @staticmethod
    def _grouper(iterable_obj, count, fillvalue=None):
        args = [iter(iterable_obj)] * count
        return zip_longest(*args, fillvalue=fillvalue)

    @staticmethod
    def draw_markers(position, box, draw, shirt=False):

        marker_padding = SHIRT_MARKER_PADDING if shirt else 0
        if position == "top":
            # TOP BORDER
            draw.line(
                (
                    box[0] + marker_padding,
                    box[1] + MARKER_INNER_OFFSET - (MARKER_PADDING if not shirt else 0),
                    box[0] + marker_padding,
                    box[1]
                    - 47
                    + MARKER_INNER_OFFSET
                    - (MARKER_PADDING if not shirt else 0),
                ),
                fill="black",
                width=2,
            )  # left
            draw.line(
                (
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - marker_padding,
                    box[1] + MARKER_INNER_OFFSET - (MARKER_PADDING if not shirt else 0),
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - marker_padding,
                    box[1]
                    - 47
                    + MARKER_INNER_OFFSET
                    - (MARKER_PADDING if not shirt else 0),
                ),
                fill="black",
                width=2,
            )  # right

        if position == "bottom":
            # BOTTOM BORDER
            draw.line(
                (
                    box[0] + marker_padding,
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[0] + marker_padding,
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    + 47
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                ),
                fill="black",
                width=2,
            )  # left
            draw.line(
                (
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - marker_padding,
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - marker_padding,
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    + 47
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                ),
                fill="black",
                width=2,
            )  # right

        if position == "left":
            # LEFT BORDER
            draw.line(
                (
                    box[0] + MARKER_INNER_OFFSET - (MARKER_PADDING if not shirt else 0),
                    box[1] + marker_padding,
                    box[0]
                    - 47
                    + MARKER_INNER_OFFSET
                    - (MARKER_PADDING if not shirt else 0),
                    box[1] + marker_padding,
                ),
                fill="black",
                width=2,
            )  # top
            draw.line(
                (
                    box[0] + MARKER_INNER_OFFSET - (MARKER_PADDING if not shirt else 0),
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - marker_padding,
                    box[0]
                    - 47
                    + MARKER_INNER_OFFSET
                    - (MARKER_PADDING if not shirt else 0),
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - marker_padding,
                ),
                fill="black",
                width=2,
            )  # bottom

        if position == "right":
            # RIGHT BORDER
            draw.line(
                (
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[1] + marker_padding,
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    + 47
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[1] + marker_padding,
                ),
                fill="black",
                width=2,
            )  # top
            draw.line(
                (
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - marker_padding,
                    box[0]
                    + (SHIRT_SIZE[0] if shirt else CARD_SIZE[0])
                    + 47
                    - MARKER_INNER_OFFSET
                    + (MARKER_PADDING if not shirt else 0),
                    box[1]
                    + (SHIRT_SIZE[1] if shirt else CARD_SIZE[1])
                    - marker_padding,
                ),
                fill="black",
                width=2,
            )  # bottom

    @staticmethod
    def _convert(obj):
        return obj.convert("RGB")

    def _create_pages(self):
        self.canvas = Image.new("RGB", self.canvas_size, color="white")
        # self.canvas = Image.new("RGB", self.canvas_size, color="black")
        self.pages += self.make_shirts_images()
        self.pages += self.make_cards_images()
        self.pages += self.make_box_image()
        self.pages += self.make_box_layout_image()

    def create_pdf(self):
        self._create_pages()
        index = [0, 3, 1, 4, 2, 5, 6, 7]
        pages = list(map(self._convert, self.pages))
        pages = [pages[i] for i in index]
        pdf = pages.pop(0)
        decks = "decks/demo" if self.deck.is_demo else "decks"
        deck_path = (
            str(self.deck.uid)
            if self.deck.is_demo
            else f"{str(self.deck.user.uid)}/{str(self.deck.uid)}"
        )
        path = os.path.join(decks, deck_path, "print_layout.pdf")
        extra_path = settings.MEDIA_ROOT / path
        pdf.save(
            extra_path,
            "PDF",
            resolution=300.0,
            save_all=True,
            append_images=pages,
        )
        return path

    def generate_card_image(self, card, web=False, for_box=False):
        def mask_image(img):
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                alpha = img.convert("RGBA").split()[-1]
                return alpha

        def place_headers(img, v, s, red=None, web=False):
            if red:
                alpha = mask_image(v)
                new_v = Image.new("RGBA", v.size, color=(255, 18, 23))
                v.paste(new_v, (0, 0), mask=alpha)

            img.paste(
                v,
                (
                    CARD_INNER_PADDING[0],
                    CARD_INNER_PADDING[1],
                ),
                mask=mask_image(v),
            )
            img.paste(
                s,
                (
                    img.size[0] - s.size[0] - CARD_INNER_PADDING[0],
                    CARD_INNER_PADDING[1],
                ),
                mask=mask_image(s),
            )
            if not web:
                s_mirror = s.rotate(180)
                v_mirror = v.rotate(180)
                img.paste(
                    v_mirror,
                    (
                        img.size[0] - v_mirror.size[0] - CARD_INNER_PADDING[0],
                        img.size[1] - v_mirror.size[1] - CARD_INNER_PADDING[1],
                    ),
                    mask=mask_image(v_mirror),
                )

                img.paste(
                    s_mirror,
                    (
                        CARD_INNER_PADDING[0],
                        img.size[1] - s_mirror.size[1] - CARD_INNER_PADDING[1],
                    ),
                    mask=mask_image(s_mirror),
                )

        card_image = Image.open(self.deck.face.images.get_value_img("bg"))
        card_image = card_image.resize(CARD_SIZE, Image.ANTIALIAS)

        if card.image.img:
            image = Image.open(card.image.img.path)
        else:
            path = settings.STATIC_ROOT / "imgs" / "cap.png"
            image = Image.open(path)
        if image.size[0] < CARD_IMAGE_SIZE[0]:
            scale = CARD_IMAGE_SIZE[0] / image.size[0]
            resize = (int(image.size[0] * scale), int(image.size[1] * scale))
            image = image.resize(resize, Image.ANTIALIAS)
        else:
            image.thumbnail(CARD_IMAGE_SIZE, Image.ANTIALIAS)

        if self.deck.mirror:
            half_image = image.crop((0, 0, image.size[0], image.size[1] // 2))
            half_image = half_image.rotate(180)
            image.paste(half_image, (0, half_image.size[1]))

        p_x = (card_image.size[0] - image.size[0]) // 2
        if not web:
            p_y = (card_image.size[1] - image.size[1]) // 2
        else:
            p_y = card_image.size[1] - image.size[1] - p_x

        img_box = (p_x, p_y)
        card_image.paste(image, img_box, mask=mask_image(image))
        header_size = (200, 200) if web else (100, 100)
        value = Image.open(self.deck.face.images.get_value_img(card.value))
        value.thumbnail(header_size, Image.ANTIALIAS)
        suit = Image.open(self.deck.face.images.get_suit_img(card.suit))
        suit.thumbnail(header_size, Image.ANTIALIAS)
        red = True if card.suit in (4, 2) else False

        place_headers(card_image, value, suit, red=red, web=web)
        if not web:
            alpha = card_image.convert("RGBA").split()[-1]

            non_transparent_card_image = Image.new(
                "RGBA",
                (card_image.size[0], card_image.size[1]),
                self.box_bg_color if for_box else self.def_bg_color,
            )
            non_transparent_card_image.paste(card_image, mask=alpha)
            card_with_margin = Image.new(
                "RGBA",
                (CARD_SIZE[0] + MARKER_PADDING, CARD_SIZE[1] + MARKER_PADDING),
                color="white",
            )
            card_with_margin.paste(non_transparent_card_image, mask=alpha)
            return non_transparent_card_image
        return card_image

    def make_cards_images(self):
        cards = self.deck.cards.filter()
        images = []
        for card in cards:
            generated_card_image = self.generate_card_image(card)
            images.append(generated_card_image)

        pages = self.make_pages_from_images(images, margin=35)
        return pages

    def make_shirts_images(self):
        margin = 0
        shirt = Image.open(
            self.deck.shirt.image.img,
        )
        shirt = shirt.resize(SHIRT_SIZE, Image.ANTIALIAS)
        images = []
        for _ in range(CARDS_COUNT):
            if shirt.mode in ("RGBA", "LA") or (
                shirt.mode == "P" and "transparency" in shirt.info
            ):
                alpha = shirt.convert("RGBA").split()[-1]
                bg = Image.new("RGBA", SHIRT_SIZE, self.def_bg_color)
                bg.paste(shirt, mask=alpha)
                images += [bg]

        promo_card = Image.open(settings.ASSETS / "card_Blank.png")
        promo_card = promo_card.resize(SHIRT_SIZE, Image.ANTIALIAS)

        images += [promo_card] * 3

        pages = self.make_pages_from_images(images, margin=margin, shirt=True)
        return pages

    def make_box_image(self):
        page = Image.new("RGBA", (3680, 2657), self.box_bg_color)
        if self.deck.box.image.img:
            box_img = Image.open(self.deck.box.image.img.path)
        else:
            card = self.deck.cards.get(value=0, suit=1)
            box_img = self.generate_card_image(card, for_box=True)
        box_img.thumbnail((614, 969), Image.ANTIALIAS)
        box_img = box_img.rotate(180)
        page.paste(box_img, (1952, 874), mask=box_img)
        return [page]

    def make_box_layout_image(self):
        img = Image.open(os.path.join(settings.STATIC_ROOT, "imgs", "box_template.png"))
        img = img.resize((3680, 2657), Image.ANTIALIAS)
        return [img]

    def make_pages_from_images(self, images, margin=None, shirt=False):
        canvas = Image.new("RGBA", self.canvas_size, self.def_bg_color)
        pages = []
        row_count = 0
        if not margin:
            margin = 0

        if not shirt:
            self.page_border_padding = (
                self.page_border_padding[0] + SHIRT_MARKER_PADDING,
                self.page_border_padding[1] + SHIRT_MARKER_PADDING,
            )

        for row in self._grouper(images, 5, None):
            if row[-1] is None and not shirt:
                row = row[::-1]

            if row_count == ROWS:
                pages += [canvas]
                canvas = Image.new("RGBA", self.canvas_size, self.def_bg_color)
                row_count = 0

            for col_count, img in enumerate(row):

                if img:

                    box = (
                        (col_count * (img.size[0] + margin))
                        + self.page_border_padding[0],
                        (row_count * (img.size[1] + margin))
                        + self.page_border_padding[1],
                    )
                    canvas.paste(img, box)
                    draw = ImageDraw.Draw(canvas)

                    # Plotter page markers
                    if row_count == 0:
                        if col_count == 0:
                            positions = ["top", "left"]
                        elif col_count == COLS - 1:
                            positions = ["top", "right"]
                        else:
                            positions = ["top"]

                    elif row_count == ROWS - 1:
                        if col_count == 0:
                            positions = ["bottom", "left"]
                        elif col_count == COLS - 1:
                            positions = ["bottom", "right"]
                        else:
                            positions = ["bottom"]

                    else:
                        if col_count == 0:
                            positions = ["left"]
                            if len(tuple(i for i in row if i is not None)) < 5:
                                positions += ["bottom"]
                        elif col_count == COLS - 1:
                            positions = ["right"]
                        else:
                            if len(tuple(i for i in row if i is not None)) < 5:
                                positions = ["bottom"]
                                if row[col_count + 1] is None:
                                    positions += ["right"]
                            else:
                                continue

                    for pos in positions:
                        self.draw_markers(position=pos, box=box, draw=draw, shirt=shirt)
            row_count += 1

        pages += [canvas]

        return pages

    def make_web_play_cards(self):
        response = {}
        resize = None
        cards = self.deck.cards.filter()
        for card in cards:
            buffered = BytesIO()
            title = "_".join([str(card.value), str(card.suit)])
            generated_card_image = self.generate_card_image(card, web=True)
            resize = tuple([(s // 3) for s in generated_card_image.size])
            generated_card_image.thumbnail(resize, Image.ANTIALIAS)
            generated_card_image.save(buffered, format="PNG")
            card_image_b64 = base64.b64encode(buffered.getvalue())
            response[title] = card_image_b64
            del buffered
        buffered = BytesIO()
        shirt = Image.open(self.deck.shirt.image.img.path)
        shirt.thumbnail(resize, Image.ANTIALIAS)
        shirt.save(buffered, format="PNG")
        response["shirt"] = base64.b64encode(buffered.getvalue())
        del buffered
        return response
