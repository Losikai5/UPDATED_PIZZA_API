from celery import Celery
from src.config import Config
from src.mail import mail,CreateMail
from typing import List
from asgiref.sync import async_to_sync

celery_app = Celery()

celery_app.config_from_object('src.config.Config')

@celery_app.task
def send_email_task(recipients: List[str], subject: str, body: str):
    message = CreateMail(recipients=recipients, subject=subject, body=body)
    async_to_sync(mail.send_message)(message)