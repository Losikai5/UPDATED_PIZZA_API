import pytest
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Standalone test suite that doesn't require full environment setup.
Tests can be run without all dependencies installed.
"""

class TestModelsStructure:
    """Test that models have the expected structure"""
    
    def test_models_file_exists(self):
        """Test that models.py file exists"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        assert models_path.exists()
    
    def test_auth_module_exists(self):
        """Test that auth module exists"""
        auth_path = Path(__file__).parent.parent / "auth"
        assert auth_path.exists()
        assert (auth_path / "service.py").exists()
    
    def test_orders_module_exists(self):
        """Test that orders module exists"""
        orders_path = Path(__file__).parent.parent / "Orders"
        assert orders_path.exists()
        assert (orders_path / "service.py").exists()
    
    def test_reviews_module_exists(self):
        """Test that reviews module exists"""
        reviews_path = Path(__file__).parent.parent / "Reviews"
        assert reviews_path.exists()
        assert (reviews_path / "service.py").exists()
    
    def test_notifications_module_exists(self):
        """Test that notifications module exists"""
        notifications_path = Path(__file__).parent.parent / "notifications"
        assert notifications_path.exists()
        assert (notifications_path / "service.py").exists()
    
    def test_admin_module_exists(self):
        """Test that admin module exists"""
        admin_path = Path(__file__).parent.parent / "Admin"
        assert admin_path.exists()
        assert (admin_path / "service.py").exists()
    
    def test_menu_module_exists(self):
        """Test that menu module exists"""
        menu_path = Path(__file__).parent.parent / "Menu"
        assert menu_path.exists()
        assert (menu_path / "service.py").exists()
    
    def test_mail_module_exists(self):
        """Test that mail module exists"""
        mail_path = Path(__file__).parent.parent / "mail.py"
        assert mail_path.exists()
    
    def test_celery_module_exists(self):
        """Test that celery module exists"""
        celery_path = Path(__file__).parent.parent / "celery.py"
        assert celery_path.exists()


class TestFileStructure:
    """Test file structure and imports"""
    
    def test_auth_has_service(self):
        """Test auth has service.py"""
        service_path = Path(__file__).parent.parent / "auth" / "service.py"
        content = service_path.read_text()
        assert "Auth_service" in content
    
    def test_orders_has_service(self):
        """Test orders has service.py"""
        service_path = Path(__file__).parent.parent / "Orders" / "service.py"
        content = service_path.read_text()
        assert "OrdersService" in content
    
    def test_reviews_has_service(self):
        """Test reviews has service.py"""
        service_path = Path(__file__).parent.parent / "Reviews" / "service.py"
        content = service_path.read_text()
        assert "ReviewsService" in content
    
    def test_notifications_has_service(self):
        """Test notifications has service.py"""
        service_path = Path(__file__).parent.parent / "notifications" / "service.py"
        content = service_path.read_text()
        assert "NotificationService" in content
    
    def test_admin_has_service(self):
        """Test admin has service.py"""
        service_path = Path(__file__).parent.parent / "Admin" / "service.py"
        content = service_path.read_text()
        assert "AdminService" in content
    
    def test_menu_has_service(self):
        """Test menu has service.py"""
        service_path = Path(__file__).parent.parent / "Menu" / "service.py"
        content = service_path.read_text()
        assert "MenuService" in content
    
    def test_mail_has_send_email(self):
        """Test mail has send_email function"""
        mail_path = Path(__file__).parent.parent / "mail.py"
        content = mail_path.read_text()
        assert "send_email" in content
    
    def test_celery_has_tasks(self):
        """Test celery has task definitions"""
        celery_path = Path(__file__).parent.parent / "celery.py"
        content = celery_path.read_text(encoding="utf-8")
        assert "send_email_task" in content
        assert "send_order_confirmation_task" in content


class TestModelsContent:
    """Test models file content"""
    
    def test_models_has_user_class(self):
        """Test models has User class"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class User" in content
    
    def test_models_has_orders_class(self):
        """Test models has Orders class"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class Orders" in content
    
    def test_models_has_reviews_class(self):
        """Test models has Reviews class"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class Reviews" in content
    
    def test_models_has_notification_class(self):
        """Test models has Notification class"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class Notification" in content
    
    def test_models_has_menuitem_class(self):
        """Test models has MenuItem class"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class MenuItem" in content
    
    def test_models_has_order_status_enum(self):
        """Test models has OrderStatus enum"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class OrderStatus" in content
        assert "pending" in content
        assert "completed" in content
    
    def test_models_has_notification_type_enum(self):
        """Test models has NotificationType enum"""
        models_path = Path(__file__).parent.parent / "db" / "models.py"
        content = models_path.read_text()
        assert "class NotificationType" in content
        assert "order_placed" in content
        assert "order_completed" in content


class TestServiceMethods:
    """Test that service classes have expected methods"""
    
    def test_auth_service_methods(self):
        """Test Auth_service has expected methods"""
        service_path = Path(__file__).parent.parent / "auth" / "service.py"
        content = service_path.read_text()
        assert "get_user_by_email" in content
        assert "create_user" in content
        assert "check_user_exists" in content
    
    def test_orders_service_methods(self):
        """Test OrdersService has expected methods"""
        service_path = Path(__file__).parent.parent / "Orders" / "service.py"
        content = service_path.read_text()
        assert "get_orders" in content
        assert "get_order_by_id" in content
        assert "create_order" in content
    
    def test_reviews_service_methods(self):
        """Test ReviewsService has expected methods"""
        service_path = Path(__file__).parent.parent / "Reviews" / "service.py"
        content = service_path.read_text()
        assert "get_reviews" in content
        assert "get_review_by_id" in content
        assert "create_review" in content
        assert "delete_review" in content
    
    def test_notifications_service_methods(self):
        """Test NotificationService has expected methods"""
        service_path = Path(__file__).parent.parent / "notifications" / "service.py"
        content = service_path.read_text()
        assert "create_notification" in content
        assert "get_user_notifications" in content
        assert "get_unread_notifications" in content
    
    def test_admin_service_methods(self):
        """Test AdminService has expected methods"""
        service_path = Path(__file__).parent.parent / "Admin" / "service.py"
        content = service_path.read_text()
        assert "get_dashboard_stats" in content
        assert "get_users" in content
        assert "get_user_by_id" in content
        assert "update_user_role" in content
    
    def test_menu_service_methods(self):
        """Test MenuService has expected methods"""
        service_path = Path(__file__).parent.parent / "Menu" / "service.py"
        content = service_path.read_text()
        assert "create_menu_item" in content
        assert "get_menu_items" in content
        assert "get_menu_item_by_id" in content
        assert "update_menu_item" in content
        assert "delete_menu_item" in content


class TestModuleImports:
    """Test that modules import expected dependencies"""
    
    def test_auth_imports_models(self):
        """Test auth service imports models"""
        service_path = Path(__file__).parent.parent / "auth" / "service.py"
        content = service_path.read_text()
        assert "from src.db.models import User" in content
    
    def test_orders_imports_models(self):
        """Test orders service imports models"""
        service_path = Path(__file__).parent.parent / "Orders" / "service.py"
        content = service_path.read_text()
        assert "Orders" in content
    
    def test_notifications_imports_models(self):
        """Test notifications service imports models"""
        service_path = Path(__file__).parent.parent / "notifications" / "service.py"
        content = service_path.read_text()
        assert "Notification" in content
    
    def test_admin_imports_models(self):
        """Test admin service imports models"""
        service_path = Path(__file__).parent.parent / "Admin" / "service.py"
        content = service_path.read_text()
        assert "User" in content
        assert "Orders" in content
        assert "Reviews" in content
