from django.conf import settings
from django.core.mail import get_connection, EmailMessage


def send_message(subj, message, email=None, alert=False):
    if not alert:
        username = settings.YANDEX_EMAIL_USER_FEEDBACK
        password = settings.YANDEX_EMAIL_USER_FEEDBACK_PASSWORD
    else:
        username = settings.YANDEX_EMAIL_USER_SERVER
        password = settings.YANDEX_EMAIL_USER_SERVER_PASSWORD

    with get_connection(
        host=settings.YANDEX_EMAIL_HOST,
        port=settings.YANDEX_EMAIL_PORT,
        username=username,
        password=password,
        use_tls=settings.EMAIL_USE_TLS,
        use_ssl=settings.EMAIL_USE_SSL,
    ) as connection:
        EmailMessage(
            subj,
            message,
            username,
            [settings.SEND_ALERT_MESSAGE_TO if not email else email],
            connection=connection,
        ).send()
