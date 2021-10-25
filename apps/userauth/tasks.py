from celery import shared_task

from time import sleep

# Send email asynchronously with a delay.
@shared_task
def send_after(duration, message):
    sleep(duration)
    message.send()
