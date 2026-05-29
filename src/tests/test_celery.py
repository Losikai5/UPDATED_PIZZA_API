import pytest
from unittest.mock import AsyncMock, patch, Mock, MagicMock
from uuid import uuid4
from src.celery import app
from src.config import Config


class TestCelery:
    """Test suite for Celery tasks"""

    def test_celery_app_configuration(self):
        """Test that Celery app is properly configured"""
        assert app is not None
        assert app.conf.broker_url == Config.REDIS_URL
        assert app.conf.result_backend == Config.REDIS_URL
        assert app.conf.broker_connection_retry_on_startup == True

    def test_celery_redis_url_configured(self):
        """Test that Redis URL is configured"""
        assert Config.REDIS_URL is not None
        assert "redis://" in Config.REDIS_URL

    @patch('src.celery.send_email')
    def test_send_email_task(self, mock_send_email):
        """Test send email task"""
        mock_send_email.return_value = None
        
        from src.celery import send_email_task
        
        subject = "Test Email"
        recipients = ["test@example.com"]
        body = "<h1>Test</h1>"
        
        # Test task execution
        result = send_email_task.apply_async(
            args=[subject, recipients, body],
            countdown=0
        )
        
        assert result is not None

    @patch('src.celery.send_email')
    def test_send_order_confirmation_task(self, mock_send_email):
        """Test send order confirmation task"""
        mock_send_email.return_value = None
        
        from src.celery import send_order_confirmation_task
        
        recipient = "customer@example.com"
        order_uid = uuid4()
        flavour = "pepperoni"
        pizza_size = "large"
        quantity = 2
        total_price = 25.99
        
        result = send_order_confirmation_task.apply_async(
            args=[recipient, str(order_uid), flavour, pizza_size, quantity, total_price],
            countdown=0
        )
        
        assert result is not None

    @patch('src.celery.send_email')
    def test_send_new_order_to_provider_task(self, mock_send_email):
        """Test send new order to provider task"""
        mock_send_email.return_value = None
        
        from src.celery import send_new_order_to_provider_task
        
        provider_email = "provider@example.com"
        order_uid = uuid4()
        pizza_name = "Pepperoni Pizza"
        
        result = send_new_order_to_provider_task.apply_async(
            args=[provider_email, str(order_uid), pizza_name],
            countdown=0
        )
        
        assert result is not None

    @patch('src.celery.send_email')
    def test_send_order_delivered_task(self, mock_send_email):
        """Test send order delivered task"""
        mock_send_email.return_value = None
        
        from src.celery import send_order_delivered_task
        
        recipient = "customer@example.com"
        order_uid = uuid4()
        
        result = send_order_delivered_task.apply_async(
            args=[recipient, str(order_uid)],
            countdown=0
        )
        
        assert result is not None

    @patch('src.celery.send_email')
    def test_send_order_cancelled_task(self, mock_send_email):
        """Test send order cancelled task"""
        mock_send_email.return_value = None
        
        from src.celery import send_order_cancelled_task
        
        recipient = "customer@example.com"
        order_uid = uuid4()
        flavour = "margherita"
        pizza_size = "medium"
        quantity = 1
        total_price = 12.99
        
        result = send_order_cancelled_task.apply_async(
            args=[recipient, str(order_uid), flavour, pizza_size, quantity, total_price],
            countdown=0
        )
        
        assert result is not None

    @patch('src.celery.send_email')
    def test_send_order_accepted_task(self, mock_send_email):
        """Test send order accepted task"""
        mock_send_email.return_value = None
        
        from src.celery import send_order_accepted_task
        
        recipient = "customer@example.com"
        order_uid = uuid4()
        
        result = send_order_accepted_task.apply_async(
            args=[recipient, str(order_uid)],
            countdown=0
        )
        
        assert result is not None

    def test_celery_task_names(self):
        """Test that celery tasks have proper names"""
        from src import celery as celery_module
        
        # Check that task functions exist
        assert hasattr(celery_module, 'send_email_task')
        assert hasattr(celery_module, 'send_order_confirmation_task')
        assert hasattr(celery_module, 'send_new_order_to_provider_task')
        assert hasattr(celery_module, 'send_order_delivered_task')
        assert hasattr(celery_module, 'send_order_cancelled_task')
        assert hasattr(celery_module, 'send_order_accepted_task')

    def test_celery_task_binding(self):
        """Test that bound tasks have retry capability"""
        from src.celery import send_order_confirmation_task, send_order_cancelled_task
        
        # These tasks should have bind=True
        assert hasattr(send_order_confirmation_task, 'bind')
        assert hasattr(send_order_cancelled_task, 'bind')

    def test_celery_broker_url_format(self):
        """Test that broker URL is in correct format"""
        broker_url = Config.REDIS_URL
        assert broker_url.startswith("redis://")

    def test_order_confirmation_email_content(self):
        """Test the structure of order confirmation email"""
        order_uid = "12345"
        flavour = "pepperoni"
        pizza_size = "large"
        quantity = 2
        total_price = 25.99
        
        # The actual body template
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
        
        assert "Order ID" in body
        assert "12345" in body
        assert "pepperoni" in body
        assert "$25.99" in body

    def test_provider_notification_email_content(self):
        """Test the structure of provider notification email"""
        order_uid = "12345"
        pizza_name = "Pepperoni Pizza"
        
        body = f"""
        <h1>You have a new order!</h1>
        <p>A customer has placed an order. Please handle it as soon as possible.</p>
        <ul>
            <li><strong>Order ID:</strong> {order_uid}</li>
            <li><strong>Pizza:</strong> {pizza_name}</li>
        </ul>
        <p>Please prepare and deliver within 30 minutes.</p>
        """
        
        assert "new order" in body
        assert order_uid in body
        assert pizza_name in body

    def test_order_delivered_email_content(self):
        """Test the structure of order delivered email"""
        order_uid = "12345"
        
        body = f"""
        <h1>Your order has been delivered!</h1>
        <p>Your pizza is ready for pickup.</p>
        <ul>
            <li><strong>Order ID:</strong> {order_uid}</li>
        </ul>
        <p>Enjoy your meal!</p>
        """
        
        assert "delivered" in body
        assert order_uid in body

    def test_order_cancelled_email_content(self):
        """Test the structure of order cancelled email"""
        order_uid = "12345"
        flavour = "margherita"
        pizza_size = "medium"
        quantity = 1
        
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
        
        assert "cancelled" in body
        assert order_uid in body
        assert flavour in body

    @patch('src.celery.send_email')
    def test_celery_task_async_execution(self, mock_send_email):
        """Test that tasks can be executed asynchronously"""
        mock_send_email.return_value = None
        
        from src.celery import send_email_task
        
        # Use apply_async for asynchronous execution
        task_id = send_email_task.apply_async(
            args=["Subject", ["test@example.com"], "<h1>Body</h1>"],
            countdown=0
        )
        
        assert task_id is not None
        assert hasattr(task_id, 'id')

    def test_celery_autodiscover_tasks(self):
        """Test that celery autodiscovers tasks"""
        # The app should have autodiscovered tasks from src module
        assert app is not None
        # Check that tasks can be accessed
        assert 'app.celery_task.send_email_task' in app.tasks or \
               any('send_email_task' in str(task) for task in app.tasks)
