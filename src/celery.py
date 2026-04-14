import os

from celery import Celery
from src.config import Config
from src.mail import send_email,mail
from asgiref.sync import async_to_sync
app = Celery('tasks', broker=Config.REDIS_URL, backend=Config.REDIS_URL)

if os.name == "nt":
    app.conf.worker_pool = "solo"


@app.task
def send_email_task(subject: str, recipients: list[str], body: str):
    async_to_sync(send_email)(subject=subject, recipients=recipients, body=body)


@app.task(name="app.celery_task.send_verification_email_task")
def send_verification_email_task(subject: str, recipients: list[str], body: str):
    async_to_sync(send_email)(subject=subject, recipients=recipients, body=body)