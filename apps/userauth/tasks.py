from celery import shared_task

from time import sleep

from django.core.mail import EmailMessage

# Send email asynchronously with a delay.
@shared_task # pyre-ignore[16] (pyre doesn't quite understand celery)
def send_after(duration: float, message: EmailMessage) -> None:
    sleep(duration)
    message.send()
