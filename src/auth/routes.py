from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from .service import Auth_service
from src.db.main import get_session
from .schemas import SignupModel, LoginModel, UserRead,UserDetailRead
from .utils import verify_hash, create_access_token, create_refresh_access_token
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, Rolechecker
from datetime import datetime, timezone
from src.db.redis import add_token_to_blocklist

auth_router = APIRouter()
auth_service = Auth_service()
roles = Rolechecker(["user", "Admin", "Staff"])

@auth_router.post("/signup")
async def signup(user_data: SignupModel, session: AsyncSession = Depends(get_session)):
    await auth_service.check_user_exists(user_data.email, session)
    new_user = await auth_service.create_user(user_data, session)
    return {"message": "User created successfully.", "user": new_user}


@auth_router.post("/login")
async def login(user_data: LoginModel, session: AsyncSession = Depends(get_session)):
    user = await auth_service.get_user_by_email(user_data.email, session)
    if user is None or not verify_hash(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong credentials")

    access_token = create_access_token({"uid": str(user.uid), "email": user.email, "role": user.role})
    refresh_token = create_refresh_access_token({"uid": str(user.uid), "email": user.email, "role": user.role})
    return JSONResponse(content={
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@auth_router.get("/refresh_token")
async def get_refresh_token(Token_details: dict = Depends(RefreshTokenBearer())):
    exp = Token_details.get("exp")
    now = datetime.now(tz=timezone.utc)
    if exp is None or now >= datetime.fromtimestamp(exp, tz=timezone.utc):
        raise HTTPException(status_code=401, detail="Token has expired")
    access_token = create_access_token({
        "uid": Token_details.get("uid"),
        "email": Token_details.get("email"),
        "role": Token_details.get("role")
    })
    return JSONResponse(content={
        "access_token": access_token
    })


@auth_router.get("/logout")
async def logout(Token_details: dict = Depends(AccessTokenBearer())):
    JTI = Token_details.get("jti")
    if JTI is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    await add_token_to_blocklist(JTI)
    return JSONResponse(content={"message": "Successfully logged out"})


@auth_router.get("/me", response_model=UserDetailRead)
async def me(current_user: dict = Depends(get_current_user), _: bool = Depends(roles)):
   return current_user            
    
