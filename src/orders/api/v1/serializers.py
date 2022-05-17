from googleapiclient import discovery
import requests
from datetime import date
from django.conf import settings
from google.oauth2 import service_account
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from game.models import Deck, DeckShirt, DeckFace
from core.utils import get_client_ip
from office.models import PromoCode
from stats.services import log_promocode_usage
from orders.models import Transaction
from icecream import ic


class PurchaseDeckSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(required=True)
    payId = serializers.CharField(source="pay_id")
    payReceiptData = serializers.CharField(source="pay_receipt_data")
    name = serializers.CharField(source="title", allow_blank=True, required=True)
    pin = serializers.CharField(required=True)
    congratulations = serializers.CharField(
        source="cong_text", allow_blank=True, required=False
    )
    isMirrorOn = serializers.BooleanField(source="mirror", required=False)
    shirtId = serializers.SlugRelatedField(
        source="shirt",
        slug_field="uid",
        required=False,
        queryset=DeckShirt.objects.all(),
    )
    faceId = serializers.SlugRelatedField(
        source="face",
        slug_field="uid",
        required=False,
        queryset=DeckFace.objects.all(),
    )
    code = serializers.CharField(required=True)

    class Meta:
        ref_name = "v1"
        model = Deck
        fields = [
            "uid",
            "payId",
            "payReceiptData",
            "name",
            "congratulations",
            "shirtId",
            "faceId",
            "pin",
            "isMirrorOn",
            "code",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.pay_type = None

    def validate_uid(self, value):
        if not value:
            raise ValidationError({"uid": ["Field must not be empty"]})
        if Deck.objects.filter(uid=value).exists():
            raise ValidationError(
                ["Deck with this uid already exists"], code="UUID_ALREADY_EXISTS"
            )
        return value

    def validate_payId(self, value):
        try:
            ta = Transaction.objects.get(pay_id=value)
        except Transaction.DoesNotExist:
            return value
        else:
            raise ValidationError(f"Transaction with id {value} already exists")

    def validate_pin(self, value):
        if len(str(value)) > 4:
            raise ValidationError("Pin length can not be larger 4 digits")
        if not str(value).isdigit():
            raise ValidationError("Pin must contain only digits")
        return value

    def validate_congratulations(self, value):
        if not value:
            return ""
        return str(value)

    def validate(self, attrs):
        pin = attrs.get("pin", None)
        if not pin:
            raise ValidationError("Pin require")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            self.user = request.user

        ta = Transaction.objects.create(
            pay_id=validated_data["pay_id"],
            pay_receipt_data=validated_data["pay_receipt_data"],
            pay_type=self.pay_type,
            pay_accepted=True,
        )
        deck = Deck.objects.create(
            uid=validated_data["uid"],
            user=self.user,
            title=validated_data.get("title", ""),
            cong_text=validated_data.get("cong_text", ""),
            face=validated_data["face"],
            shirt=validated_data["shirt"],
            pin=validated_data["pin"],
            mirror=validated_data.get("mirror"),
            transaction=ta,
        )
        return deck


class PurchaseDeckGoogleSerializer(PurchaseDeckSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pay_type = 2

    def validate(self, attrs):
        attrs = super().validate(attrs)
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_FILE_PATH
        )
        service = discovery.build("androidpublisher", "v3", credentials=credentials)
        input_pay_id = attrs["pay_id"]
        pay_receipt_data = attrs["pay_receipt_data"]

        result = (
            service.purchases()
            .products()
            .get(
                packageName=settings.GOOGLE_ANDROID_PUBLISHER_APP,
                productId=input_pay_id,
                token=pay_receipt_data,
            )
            .execute()
        )
        if result["purchaseState"] == 0:
            order_id = result["orderId"]
            attrs["pay_id"] = order_id
        elif result["purchaseState"] == 1:
            raise ValidationError(code="ERROR", detail={"status": ["CANCELED"]})
        else:
            raise ValidationError(code="ERROR", detail={"status": ["PENDING"]})
        return attrs


class PurchaseDeckAppleSerializer(PurchaseDeckSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pay_type = 3

    @staticmethod
    def get_apple_response(value):
        headers = {
            "content-type": "application/json",
        }

        payload = {
            "receipt-data": value,
            "exclude-old-transactions": True,
        }

        req = requests.post(settings.APPLE_APP_STORE_URL, json=payload, headers=headers)
        response = req.json()
        if response["status"] == 21007:
            req = requests.post(
                settings.APPLE_APP_STORE_SANDBOX_URL, json=payload, headers=headers
            )
            response = req.json()

        return response

    def validate(self, attrs):
        attrs = super().validate(attrs)
        data = attrs["pay_receipt_data"]
        input_pay_id = attrs["pay_id"]
        response = self.get_apple_response(data)
        resp_pay_id = response["receipt"]["in_app"][0]["transaction_id"]
        if input_pay_id != resp_pay_id:
            raise ValidationError({"payId": ["Invalid pay_id!"]})
        if (
            response["receipt"]["in_app"][0]["product_id"]
            != settings.APPLE_IN_APP_PURCHASES_ID
        ):
            raise ValidationError({"receipt-data": ["Invalid product_id"]})
        return attrs


class PurchaseDeckPromoSerializer(PurchaseDeckSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pay_type = 1

    def validate_code(self, value):
        code = value.upper()
        qs = PromoCode.objects.filter()
        request = self.context["request"]
        user = request.user

        if not qs.filter(code=code).exists():
            raise ValidationError(
                code="PROMO_CODE_INVALID",
                detail={"code": ["Promocode invalid"]},
            )

        try:
            promocode = qs.filter(
                start_date__lte=date.today(), end_date__gte=date.today()
            ).get(code=code)
        except PromoCode.DoesNotExist:
            raise ValidationError(
                code="PROMO_CODE_EXPIRED",
                detail={"code": ["Promocode expired"]},
            )
        if not promocode.check_usability:
            raise ValidationError(
                code="PROMO_CODE_UNUSABLE",
                detail={"code": ["Promocode reached max usages"]},
            )

        if promocode.limit != 0 and promocode.usages.filter(user=user).exists():
            raise ValidationError(
                code="PROMO_CODE_ALREADY_USED",
                detail={"code": ["User reached limit of usages"]},
            )
        if promocode.discount != 100:
            raise ValidationError(
                code="PROMO_CODE_INVALID",
                detail={"code": ["Promocode invalid"]},
            )
        return promocode

    def create(self, validated_data):
        if not validated_data.get("code"):
            raise ValidationError({"code": ["Field can't be Empty"]})
        validated_data["pay_id"] = ""
        validated_data["pay_receipt_data"] = ""
        promocode = validated_data.pop("code")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            self.user = request.user
        if promocode.discount == promocode.Discount.D100:
            ta = Transaction.objects.create(
                pay_type=self.pay_type,
                promocode=promocode,
                pay_accepted=True,
            )

            deck = Deck.objects.create(
                uid=validated_data["uid"],
                user=self.user,
                title=validated_data.get("title", ""),
                cong_text=validated_data.get("cong_text", ""),
                face=validated_data["face"],
                shirt=validated_data["shirt"],
                pin=validated_data["pin"],
                mirror=validated_data.get("mirror"),
                transaction=ta,
            )
            log_promocode_usage(
                self.user, get_client_ip(self.context["request"]), promocode
            )
            return deck
        else:
            raise ValidationError(
                code="NEED_APP_UPDATE",
                detail={"code": ["Update your app for using this promo code"]},
            )
