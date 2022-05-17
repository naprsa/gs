from celery.app import shared_task

from core.services import send_message


@shared_task
def send_feedback_answer(subj, message, email):
    send_message(subj, message, email, alert=False)
    return "message sent"
