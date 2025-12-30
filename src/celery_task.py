from celery import Celery
from src.config import Config
from src.mail import mail, CreateMail
from typing import List
from asgiref.sync import async_to_sync
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app with broker and backend
celery_app = Celery(
    'pizza_api',
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    result_expires=3600,  # Results expire after 1 hour
    broker_connection_retry_on_startup=True,
)

@celery_app.task(
    bind=True,
    name='send_email_task',
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 minutes between retries
    retry_jitter=True
)
def send_email_task(self, recipients: List[str], subject: str, body: str):
    """
    Asynchronous task to send emails using FastAPI-Mail.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: HTML email body
        
    Returns:
        dict: Status of email sending
        
    Raises:
        Exception: If email sending fails after all retries
    """
    try:
        logger.info(f"Sending email to {recipients} with subject: {subject}")
        
        # Create email message
        message = CreateMail(recipients=recipients, subject=subject, body=body)
        
        # Send email asynchronously (convert async to sync for Celery)
        async_to_sync(mail.send_message)(message)
        
        logger.info(f"Email sent successfully to {recipients}")
        return {
            "status": "success",
            "recipients": recipients,
            "subject": subject
        }
        
    except Exception as exc:
        logger.error(f"Failed to send email to {recipients}: {str(exc)}")
        
        # Retry the task
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for email to {recipients}")
            return {
                "status": "failed",
                "recipients": recipients,
                "error": str(exc)
            }
