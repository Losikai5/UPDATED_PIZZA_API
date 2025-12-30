from sqlalchemy import false
from src.auth.schemas import SignupModel


auth_prefix = f"/api/v2/auth"
def test_user_creation(fake_db_session, fake_user_service,client):
    signup_data = {
  "email": "johndoe@example.com",
  "first_name": "John",
  "is_verified": false,
  "last_name": "Doe",
  "password": "strongpassword123",
  "role": "user",
  "username": "johndoe"
}
    user_data = SignupModel(**signup_data)    

    response = client.post(
        url=f"{auth_prefix}/signup/", 
        json=signup_data)

    
    assert fake_user_service.check_user_exists_called_once()
    assert fake_user_service.create_user_called_once(signup_data['email'],fake_db_session)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once(signup_data,fake_db_session)