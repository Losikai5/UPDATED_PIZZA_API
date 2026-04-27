import os

from celery import Celery
from src.config import Config
from src.mail import send_email
from asgiref.sync import async_to_sync

app = Celery("src")

app.conf.update(
    broker_url=Config.REDIS_URL,
    result_backend=Config.REDIS_URL,
    broker_connection_retry_on_startup=True,
)

if os.name == "nt":
    app.conf.worker_pool = "solo"

app.autodiscover_tasks(["src"])


@app.task(name="app.celery_task.send_email_task")
def send_email_task(subject: str, recipients: list[str], body: str):
    async_to_sync(send_email)(subject=subject, recipients=recipients, body=body)

# Order confirmation email — sent to the user when they place an order
@app.task(bind=True, name="src.celery_task.send_order_confirmation_task")
def send_order_confirmation_task(self, recipient: str, order_uid: str, flavour: str, pizza_size: str, quantity: int, total_price: float):
    try:
        subject = "Order Confirmation - Pizza is on the way! 🍕"
        body = f"""
        <h1>Your order has been received!</h1>
        <p>Here are your order details:</p>
        <ul>
            <li><strong>Order ID:</strong> {order_uid}</li>
            <li><strong>Flavour:</strong> {flavour}</li>
            <li><strong>Size:</strong> {pizza_size}</li>
            <li><strong>Quantity:</strong> {quantity}</li>
            <li><strong>Total Price:</strong> ${total_price:.2f}</li>
        </ul>
        <p>Please wait 30 minutes for your pizza!</p>
        """
        async_to_sync(send_email)(subject=subject, recipients=[recipient], body=body)
    except Exception as exc:
        raise self.retry(exc=exc)


# New order notification — sent to the provider when an order is placed
@app.task(name="src.celery_task.send_new_order_to_provider_task")
def send_new_order_to_provider_task(provider_email: str, order_uid: str, pizza_name: str):
    subject = "New Order Received!"
    body = f"""
    <h1>You have a new order!</h1>
    <p>A customer has placed an order. Please handle it as soon as possible.</p>
    <ul>
        <li><strong>Order ID:</strong> {order_uid}</li>
        <li><strong>Pizza:</strong> {pizza_name}</li>
    </ul>
    <p>Please prepare and deliver within 30 minutes.</p>
    """
    async_to_sync(send_email)(subject=subject, recipients=[provider_email], body=body)


# Order delivered notification — sent to the user when provider marks order as delivered
@app.task(name="src.celery_task.send_order_delivered_task")
def send_order_delivered_task(recipient: str, order_uid: str):
    subject = "Your Pizza has been Delivered!"
    body = f"""
    <h1>Your order has been delivered!</h1>
    <p>Your pizza is ready for pickup.</p>
    <ul>
        <li><strong>Order ID:</strong> {order_uid}</li>
    </ul>
    <p>Enjoy your meal!</p>
    """
    async_to_sync(send_email)(subject=subject, recipients=[recipient], body=body)


@app.task(name="src.celery_task.send_order_cancelled_task", bind=True, max_retries=3, default_retry_delay=60)
def send_order_cancelled_task(self, recipient: str, order_uid: str, flavour: str, pizza_size: str, quantity: int, total_price: float):
    try:
        subject = "Order Cancelled ❌"
        body = f"""
        <h1>An order has been cancelled!</h1>
        <p>A customer has cancelled their order. Here are the details:</p>
        <ul>
            <li><strong>Order ID:</strong> {order_uid}</li>
            <li><strong>Flavour:</strong> {flavour}</li>
            <li><strong>Size:</strong> {pizza_size}</li>
            <li><strong>Quantity:</strong> {quantity}</li>
        </ul>
        <p>Please disregard this order.</p>
        """
        async_to_sync(send_email)(subject=subject, recipients=[Config.PROVIDER_EMAIL], body=body) 
    except Exception as exc:
            raise self.retry(exc=exc)  
    

@app.task(name="src.celery_task.send_order_accepted_task", bind=True, max_retries=3, default_retry_delay=60)
def send_order_accepted_task(self, recipient: str, order_uid: str):
    try:
        subject = "Your order is being prepared! 👨‍🍳"
        body = f"""
        <h1>Great news!</h1>
        <p>Your order <strong>{order_uid}</strong> has been accepted and is now being prepared.</p>
        <p>Please wait while we make your pizza!</p>
        """
        async_to_sync(send_email)(subject=subject, recipients=[recipient], body=body)
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(name="src.celery_task.send_order_in_transit_task", bind=True, max_retries=3, default_retry_delay=60)
def send_order_in_transit_task(self, recipient: str, order_uid: str):
    try:
        subject = "Your pizza is on the way! 🚗"
        body = f"""
        <h1>Your pizza is on the way!</h1>
        <p>Your order <strong>{order_uid}</strong> is now in transit.</p>
        <p>Please be ready to receive your delivery!</p>
        """
        async_to_sync(send_email)(subject=subject, recipients=[recipient], body=body)
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(name="src.celery_task.send_order_completed_task", bind=True, max_retries=3, default_retry_delay=60)
def send_order_completed_task(self, recipient: str, order_uid: str):
    try:
        subject = "Your pizza has been delivered! 🍕"
        body = f"""
        <h1>Enjoy your meal!</h1>
        <p>Your order <strong>{order_uid}</strong> has been delivered successfully.</p>
        <p>Thank you for ordering with us! Please leave a review.</p>
        """
        async_to_sync(send_email)(subject=subject, recipients=[recipient], body=body)
    except Exception as exc:
        raise self.retry(exc=exc)
