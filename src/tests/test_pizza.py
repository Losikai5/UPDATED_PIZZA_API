#from src.tests.conftest import fake_db_session, fake_pizza_service


orders_prefix = f"/api/v2/orders"
def test_get_all_orders(fake_db_session, fake_pizza_service, client):
    response = client.get(f"{orders_prefix}")

    assert fake_pizza_service.get_all_pizzas_called_once()
    assert fake_pizza_service.get_all_pizzas_called_once(fake_db_session)