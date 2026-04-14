from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from .utils import decode_token
from fastapi import Depends, Request,HTTPException
from src.db.redis import is_token_revoked
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import Auth_service
Service = Auth_service()

class Bearer_token(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    async def __call__(self, request:Request)->HTTPAuthorizationCredentials:
         creds = await super().__call__(request) 
         if not creds:
            raise HTTPException(status_code=403, detail="Missing credentials")

         token = creds.credentials
         token_data = decode_token(token)

        # Reject None, empty dict, or False
         if not token_data:
            raise HTTPException(status_code=403, detail="Invalid or expired token")
         
         if await is_token_revoked(token_data.get("jti")):
            raise HTTPException(status_code=403, detail="Token has been revoked")
         
        

        # Token type check (IMPORTANT)
         await self.verify_token_type(token_data)
         return token_data
    

    async def verify_token_type(self, token_data: dict):
        raise NotImplementedError("Subclasses must implement verify_token_type")


class AccessTokenBearer(Bearer_token):
    async def verify_token_type(self, token_data: dict):
        if token_data.get("refresh", False):  # If it IS a refresh token
            raise HTTPException(status_code=403, detail="Access token needed")

class RefreshTokenBearer(Bearer_token):
    async def verify_token_type(self, token_data: dict):
        if not token_data.get("refresh", False):  # If it's NOT a refresh token
            raise HTTPException(status_code=403, detail="Refresh token needed")

async def get_current_user(token_data:dict = Depends(AccessTokenBearer()),session:AsyncSession = Depends(get_session)):
               user_email = token_data["user"]["email"]
               current_user = await Service.get_user_by_email(user_email,session)
               if not current_user:
                   raise HTTPException(status_code=404,detail="User not found!!!!!!")
               return current_user      
        
class Rolechecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user = Depends(get_current_user)):
        user_role = user.role
        if user_role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")  
        if not user.is_verified:
            raise HTTPException(status_code=403, detail="Email not verified")
        return True      



