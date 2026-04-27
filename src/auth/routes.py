from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from .service import Auth_service
from src.db.main import get_session
from src.celery import send_email_task
from .schemas import (
    SignupModel,
    LoginModel,
    UserRead,
    UserDetailRead,
    EmailModel,
    SignupSuccessResponse,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    TokenPairResponse,
    AccessTokenResponse,
    MessageResponse,
)
from .utils import verify_hash, create_access_token, create_refresh_access_token,create_url_safe_token,decode_url_safe_token,create_hash
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, Rolechecker
from datetime import datetime, timezone
from src.db.redis import add_token_to_blocklist
from src.config import Config

auth_router = APIRouter()
auth_service = Auth_service()
roles = Rolechecker(["user", "Admin", "Staff"])

@auth_router.post("/signup", response_model=SignupSuccessResponse)
async def signup(user_data: SignupModel, session: AsyncSession = Depends(get_session)):
    await auth_service.check_user_exists(user_data.email, session)
    new_user = await auth_service.create_user(user_data, session)
    token = create_url_safe_token({"email": new_user.email})
    link = f"http://{Config.DOMAIN}/api/v2/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    send_email_task.delay(subject="Verify your email", recipients=[new_user.email], body=html_message)
    return {
        "message": "User created successfully please verify your email.",
        "user": UserRead.model_validate(new_user),
    }
@auth_router.get("/verify/{token}", response_model=MessageResponse)
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    data = decode_url_safe_token(token)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid verification payload")

    user = await auth_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await auth_service.update_user(user, {"is_verified": True}, session)
    return {"message": "Email verified successfully"}

@auth_router.post("/login", response_model=TokenPairResponse)
async def login(user_data: LoginModel, session: AsyncSession = Depends(get_session)):
    user = await auth_service.get_user_by_email(user_data.email, session)
    if user is None or not verify_hash(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")

    token_payload = {
        "uid": str(user.uid),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_access_token(token_payload)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@auth_router.get("/refresh_token", response_model=AccessTokenResponse)
async def get_refresh_token(Token_details: dict = Depends(RefreshTokenBearer())):
    exp = Token_details.get("exp")
    now = datetime.now(tz=timezone.utc)
    if exp is None or now >= datetime.fromtimestamp(exp, tz=timezone.utc):
        raise HTTPException(status_code=401, detail="Token has expired")
    user_details = Token_details.get("user", {})
    access_token = create_access_token({
        "uid": user_details.get("uid"),
        "email": user_details.get("email"),
        "role": user_details.get("role")
    })
    return {
        "access_token": access_token
    }


@auth_router.get("/logout", response_model=MessageResponse)
async def logout(Token_details: dict = Depends(AccessTokenBearer())):
    JTI = Token_details.get("jti")
    if JTI is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    await add_token_to_blocklist(JTI)
    return {"message": "Successfully logged out"}


@auth_router.get("/me", response_model=UserDetailRead)
async def me(current_user: dict = Depends(get_current_user), _: bool = Depends(roles)):
   return current_user     

@auth_router.post('/send_mail', response_model=MessageResponse)
async def send_mail(email_data: EmailModel):
       emails = email_data.addresses
       html = "<h1>Welcome to Losika Pizza</h1><p>Thank you for signing up! We're excited to have you on board.</p>"
       subject = "Welcome to Losika Pizza!"
       send_email_task.delay(subject=subject, recipients=emails, body=html)
       return {"message": "Email sent successfully to the provided addresses."}

@auth_router.post('/password_reset', response_model=MessageResponse)
async def password_reset(email_data: PasswordResetRequestModel, session: AsyncSession = Depends(get_session)):
    email = email_data.email
    user = await auth_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_url_safe_token({"email": user.email})
    link = f"http://{Config.DOMAIN}/api/v2/auth/reset-password?token={token}"

    html_message = f"""
    <h1>Password Reset Request</h1>
    <p>Please click this <a href="{link}">link</a> to reset your password. This link will expire in 1 hour.</p>
    """
    send_email_task.delay(subject="Password Reset Request", recipients=[user.email], body=html_message)
    return {"message": "Password reset email sent successfully."}


@auth_router.get("/reset-password", response_model=MessageResponse)
async def reset_password_info(token: str):
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    return {"message": "Token received. Submit your new password to this same route using POST."}


@auth_router.post("/reset-password", response_model=MessageResponse)
async def reset_password_with_query_token(
    token: str,
    password_data: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    return await password_reset_confirm(token, password_data, session)

@auth_router.post("/password-reset-confirm/{token}", response_model=MessageResponse)
async def password_reset_confirm(token: str, password_data: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    data = decode_url_safe_token(token)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    user = await auth_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password_hash = create_hash(password_data.new_password)
    await auth_service.update_user(user, {"password_hash": new_password_hash}, session)
    return {"message": "Password reset successfully"}
    
