# pyre-strict
from celery import shared_task

from time import sleep

from django.core.mail import EmailMessage

# Send email asynchronously with a delay.
@shared_task
def send_after(duration: float, message: EmailMessage) -> None:
    sleep(duration)
    message.send()
