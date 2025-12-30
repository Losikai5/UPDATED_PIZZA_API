from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.config import Config
from .service import Auth_service
from src.db.main import get_session
from .schemas import SignupModel,LoginModel,UserRead,EmailModel,PasswordResetModel,PasswordResetConfirmModel
from .utils import Verify_hash,create_access_token,create_refresh_access_token,generate_email_verification_token,verify_email_verification_token,Create_hash
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer, get_current_user, Rolechecker
from datetime import datetime, timezone
from src.db.redis import add_token_to_blocklist
from src.mail import mail,CreateMail
#from src.celery_task import send_email_task

auth_router = APIRouter()
auth_service = Auth_service()
roles = Rolechecker(["user","admin","staff"])
workers_role = Depends(Rolechecker(["admin","staff"]))


@auth_router.post("/send_verification_email")
async def Send_verification_email(emails:EmailModel):
    email = emails.Addresses
    html = "<p>Please click the link below to verify your email address:</p>"
    message = CreateMail(recipients=email, subject="Email Verification", body=html)
    await mail.send_message(message)
    return JSONResponse(content={"message": "Verification email sent"},status_code=200)


@auth_router.get("/verify_email/{token}")
async def Verify_email(token:str,session:AsyncSession=Depends(get_session)):
    data = verify_email_verification_token(token)
    if not data:
        raise HTTPException(status_code=400,detail="Invalid or expired token")
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400,detail="Invalid token data")
    user = await auth_service.get_user_by_email(email,session)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    await auth_service.update_user(user,{"is_verified":True},session)
    return JSONResponse(content={"message": "Email verified successfully"},status_code=200)
    
    


@auth_router.post("/signup")
async def Signup(user_data:SignupModel,session:AsyncSession=Depends(get_session)):
      user =  await auth_service.check_user_exists(user_data.email,session)
      if user is not None:
           raise HTTPException(status_code=403,detail="User email already exists")
      new_user = await auth_service.create_user(user_data,session)

      token = generate_email_verification_token({"email": new_user.email})
      link = f"http://{Config.DOMAIN}/api/v2/auth/verify_email/{token}"
      html = f"<h1>Welcome {new_user.first_name},</h1><p>Thank you for signing up. Please verify your email address to activate your account here <a href='{link}'>this link</a>.</p>"
      message = CreateMail(recipients=[new_user.email], subject="Welcome to Our Service - Verify Your Email", body=html)
      await mail.send_message(message)
      return {"message": "User created successfully. Please check your email to verify your account.","user":new_user}


@auth_router.post("/login")
async def Login(user_data:LoginModel,session:AsyncSession=Depends(get_session)):
     user = await auth_service.get_user_by_email(user_data.email,session)
     if user is  None or not Verify_hash(user_data.password,user.password_hash):
          raise HTTPException(status_code=401,detail="wrong credentials")
     
     access_token = create_access_token({"uid": str(user.uid), "email": user.email, "role": user.role})
     refresh_token = create_refresh_access_token({"uid": str(user.uid), "email": user.email, "role": user.role})
     return JSONResponse(content={
           "access_token":access_token,
             "refresh_token":refresh_token
      }) 


@auth_router.get("/refresh_token")
async def Get_refesh_token(Token_details:dict =Depends(RefreshTokenBearer())):
     exp = Token_details.get("exp")
     now = datetime.now(tz=timezone.utc)
     if exp is None or now >= datetime.fromtimestamp(exp,tz=timezone.utc):
          raise HTTPException(status_code=401,detail="Token has expired")
     access_token = create_access_token({"uid": Token_details.get("uid"), "email": Token_details.get("email"), "role": Token_details.get("role")})
     return JSONResponse(content={
           "access_token": access_token
      })


@auth_router.get("/logout")
async def Logout(Token_details:dict =Depends(AccessTokenBearer())):
     JTI = Token_details.get("jti")
     if JTI is None:
          raise HTTPException(status_code=401,detail="Invalid token")
     await add_token_to_blocklist(JTI)
     return JSONResponse(content={"message": "Successfully logged out"})


@auth_router.get("/me",response_model=UserRead)
async def Me(current_user: dict = Depends(get_current_user),_:bool=Depends(Rolechecker(workers_role))):
    return current_user


@auth_router.post("/password-reset-request")
async def Password_reset(email:PasswordResetModel,session:AsyncSession=Depends(get_session)):
    user = await auth_service.get_user_by_email(email.email,session)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    token = generate_email_verification_token({"email": user.email})
    link = f"http://{Config.DOMAIN}/api/v2/auth/password-reset-confirm/{token}"
    html = f"<p>Please click the link below to reset your password:</p><a href='{link}'>Reset Password</a>"
    message = CreateMail(recipients=[user.email], subject="Password Reset Request", body=html)
    await mail.send_message(message)
    return JSONResponse(content={"message": "Password reset email sent"},status_code=200)


@auth_router.post("/password-reset-confirm/{token}")
async def Password_reset_confirm(token:str,new_password:PasswordResetConfirmModel,session:AsyncSession=Depends(get_session)):
    if new_password.new_password != new_password.confirm_password:
        raise HTTPException(status_code=400,detail="Passwords do not match")
    
    data = verify_email_verification_token(token)
    if not data:
        raise HTTPException(status_code=400,detail="Invalid or expired token")
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400,detail="Invalid token data")
    user = await auth_service.get_user_by_email(email,session)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    hashed_password = Create_hash(new_password.new_password)
    await auth_service.update_user(user,{"password_hash":hashed_password},session)
    return JSONResponse(content={"message": "Password has been reset successfully"},status_code=200)