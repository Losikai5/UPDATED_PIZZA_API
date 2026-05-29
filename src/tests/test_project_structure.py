"""
Simple test that verifies the project structure and content 
without importing the src package or any routes.
"""
import pytest
from pathlib import Path


def test_modules_exist():
    """Test that all required modules exist"""
    base_path = Path(__file__).parent.parent
    
    modules = [
        "auth",
        "Orders",
        "Reviews",
        "notifications",
        "Admin",
        "Menu",
        "db",
        "Addresse",
        "Cart"
    ]
    
    for module in modules:
        module_path = base_path / module
        assert module_path.exists(), f"Module {module} does not exist"
        assert (module_path / "__init__.py").exists(), f"Module {module} missing __init__.py"


def test_service_files_exist():
    """Test that all service.py files exist in modules"""
    base_path = Path(__file__).parent.parent
    
    services = [
        "auth/service.py",
        "Orders/service.py",
        "Reviews/service.py",
        "notifications/service.py",
        "Admin/service.py",
        "Menu/service.py",
        "db/main.py",
    ]
    
    for service in services:
        service_path = base_path / service
        assert service_path.exists(), f"Service {service} does not exist"


def test_mail_module_exists():
    """Test that mail.py exists"""
    base_path = Path(__file__).parent.parent
    mail_path = base_path / "mail.py"
    assert mail_path.exists(), "mail.py does not exist"


def test_celery_module_exists():
    """Test that celery.py exists"""
    base_path = Path(__file__).parent.parent
    celery_path = base_path / "celery.py"
    assert celery_path.exists(), "celery.py does not exist"


def test_config_module_exists():
    """Test that config.py exists"""
    base_path = Path(__file__).parent.parent
    config_path = base_path / "config.py"
    assert config_path.exists(), "config.py does not exist"


def test_db_models_exists():
    """Test that db/models.py exists"""
    base_path = Path(__file__).parent.parent
    models_path = base_path / "db" / "models.py"
    assert models_path.exists(), "db/models.py does not exist"


def test_service_has_required_classes():
    """Test that service files contain the expected classes"""
    base_path = Path(__file__).parent.parent
    
    service_checks = {
        "auth/service.py": "Auth_service",
        "Orders/service.py": "OrdersService",
        "Reviews/service.py": "ReviewsService",
        "notifications/service.py": "NotificationService",
        "Admin/service.py": "AdminService",
        "Menu/service.py": "MenuService",
    }
    
    for service_file, class_name in service_checks.items():
        service_path = base_path / service_file
        content = service_path.read_text()
        assert f"class {class_name}" in content, f"{class_name} not found in {service_file}"


def test_models_file_content():
    """Test that models.py contains expected classes"""
    base_path = Path(__file__).parent.parent
    models_path = base_path / "db" / "models.py"
    content = models_path.read_text()
    
    required_classes = [
        "class User",
        "class Orders",
        "class Reviews",
        "class Notification",
        "class MenuItem",
        "class MenuItemSize",
    ]
    
    for required_class in required_classes:
        assert required_class in content, f"{required_class} not found in models.py"


def test_models_have_enums():
    """Test that models.py contains required enums"""
    base_path = Path(__file__).parent.parent
    models_path = base_path / "db" / "models.py"
    content = models_path.read_text()
    
    enums = [
        "class OrderStatus",
        "class NotificationType",
        "class PizzaSize",
    ]
    
    for enum in enums:
        assert enum in content, f"{enum} not found in models.py"


def test_mail_has_send_email_function():
    """Test that mail.py has send_email function"""
    base_path = Path(__file__).parent.parent
    mail_path = base_path / "mail.py"
    content = mail_path.read_text()
    assert "async def send_email" in content, "send_email function not found in mail.py"


def test_celery_has_task_definitions():
    """Test that celery.py has task definitions"""
    base_path = Path(__file__).parent.parent
    celery_path = base_path / "celery.py"
    content = celery_path.read_text(encoding="utf-8")
    
    required_tasks = [
        "send_email_task",
        "send_order_confirmation_task",
        "send_new_order_to_provider_task",
        "send_order_delivered_task",
        "send_order_cancelled_task",
        "send_order_accepted_task",
    ]
    
    for task in required_tasks:
        assert task in content, f"{task} not found in celery.py"


def test_config_has_settings_class():
    """Test that config.py has Settings class"""
    base_path = Path(__file__).parent.parent
    config_path = base_path / "config.py"
    content = config_path.read_text()
    assert "class Settings" in content, "Settings class not found in config.py"


def test_auth_service_methods():
    """Test that auth service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "auth" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "get_user_by_email",
        "create_user",
        "check_user_exists",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in auth service"


def test_orders_service_methods():
    """Test that orders service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "Orders" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "get_orders",
        "create_order",
        "get_order_by_id",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in orders service"


def test_reviews_service_methods():
    """Test that reviews service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "Reviews" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "get_reviews",
        "create_review",
        "get_review_by_id",
        "delete_review",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in reviews service"


def test_notifications_service_methods():
    """Test that notifications service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "notifications" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "create_notification",
        "get_user_notifications",
        "get_unread_notifications",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in notifications service"


def test_admin_service_methods():
    """Test that admin service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "Admin" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "get_dashboard_stats",
        "get_users",
        "get_user_by_id",
        "update_user_role",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in admin service"


def test_menu_service_methods():
    """Test that menu service has required methods"""
    base_path = Path(__file__).parent.parent
    service_path = base_path / "Menu" / "service.py"
    content = service_path.read_text()
    
    required_methods = [
        "create_menu_item",
        "get_menu_items",
        "get_menu_item_by_id",
        "update_menu_item",
        "delete_menu_item",
    ]
    
    for method in required_methods:
        assert f"async def {method}" in content or f"def {method}" in content, \
            f"{method} not found in menu service"


def test_migration_files_exist():
    """Test that migration files exist"""
    migrations_path = Path(__file__).parent.parent.parent / "migrations"
    assert migrations_path.exists(), "migrations directory does not exist"
    assert (migrations_path / "versions").exists(), "migrations/versions directory does not exist"


def test_test_files_created():
    """Test that all test files were created"""
    tests_path = Path(__file__).parent
    
    required_tests = [
        "test_auth.py",
        "test_orders.py",
        "test_reviews.py",
        "test_notifications.py",
        "test_admin.py",
        "test_menu.py",
        "test_mail.py",
        "test_celery.py",
        "test_db.py",
        "test_structure.py",
    ]
    
    for test_file in required_tests:
        test_path = tests_path / test_file
        assert test_path.exists(), f"Test file {test_file} was not created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
