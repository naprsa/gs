import io
import json
import hashlib
import zipfile
import os
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
import jsonschema
from jsonschema import validate
from PIL import Image as IMG

from game.models import DeckFace, Image, ImageCollection, DeckFacesJsonSchema


class DeckFaceAdminForm(forms.ModelForm):
    file = forms.FileField()
    valid_extensions = ["png", "jpg"]

    class Meta:
        model = DeckFace
        fields = [
            # "version",
            "title",
            "file",
        ]

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file and "zip" not in file.name.split(".")[-1]:
            raise ValidationError("File must be an zip archive!")
        return file

    @staticmethod
    def validate_json(json):
        schema = DeckFacesJsonSchema.objects.filter()[0].json
        try:
            validate(instance=json, schema=schema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True

    @staticmethod
    def images_md5(images):
        hash = hashlib.md5()
        for image in images:
            im = image.img.open()
            img = IMG.open(im)
            hash.update(img.tobytes())
        return hash.hexdigest()

    def validate_images(self, archive):
        prev_size_values = None
        prev_size_suits = None
        values = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "A",
            "J",
            "K",
            "Q",
            "с_2",
            "с_3",
            "с_4",
            "с_5",
            "с_6",
            "с_7",
            "с_8",
            "с_9",
            "с_10",
            "с_A",
            "с_J",
            "с_K",
            "с_Q",
        ]
        suits = ["clubs", "hearts", "diamonds", "spades"]
        for file in archive.namelist():
            if (
                not ("/" in file or file.startswith((".", "_", "__")))
                and file.split(".")[-1].lower() in self.valid_extensions
            ):
                im = archive.read(file)
                img = IMG.open(io.BytesIO(im))
                if file.split(".")[0].lower() in values:
                    if prev_size_values and img.size != prev_size_values:
                        return False
                    else:
                        prev_size_values = img.size

                elif file.split(".")[0].lower() in suits:
                    if prev_size_suits and img.size != prev_size_suits:
                        return False
                    else:
                        prev_size_suits = img.size
                else:
                    continue
        return True

    def save(self, *args, **kwargs):
        input_zip = self.cleaned_data["file"]

        path = os.path.join(
            settings.MEDIA_ROOT, "stuff", "faces", str(self.instance.uid)
        )
        if self.instance and self.instance.pk:
            self.instance.images.images.all().delete()
        with zipfile.ZipFile(input_zip, "r") as archive:
            if "info.json" not in archive.namelist():
                raise ValidationError("Archive must contain 'info.json'")

            if not self.validate_images(archive):
                raise ValidationError("Error! Please, check size(px) of images.")

            images = [
                file
                for file in archive.namelist()
                if not ("/" in file or file.startswith((".", "_", "__")))
                and file.split(".")[-1].lower() in self.valid_extensions
            ]
            archive.extractall(path)

        if self.instance and not self.instance.pk:
            collection = ImageCollection.objects.create()
            self.instance.images = collection

        self.instance.images.get_collection_qs().delete()

        with open(os.path.join(path, "info.json")) as f:
            json_db = json.load(f)
            if not self.validate_json(json_db):
                raise ValidationError(
                    "JSON validation fail! Please check 'info.json' from the archive"
                )
            self.instance.json_settings = json_db

        image_objs = [
            Image(
                img=f"stuff/faces/{str(self.instance.uid)}/{image}",
                collection=self.instance.images,
            )
            for image in images
        ]

        images = Image.objects.bulk_create(image_objs)
        self.instance.md5 = self.images_md5(images)

        return super().save(*args, **kwargs)
