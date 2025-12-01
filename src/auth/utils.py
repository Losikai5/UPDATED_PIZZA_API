from passlib.context  import CryptContext
import jwt
from datetime import timedelta,datetime
import uuid
import logging
from src.config import Config

pwd_hash = CryptContext(schemes=["bcrypt"],deprecated = "auto")
ACCESS_TIME_MINUTES = 60

def Create_hash(password:str):
    return pwd_hash.hash(password)
def Verify_hash(password:str,Create_hash:str):
     return pwd_hash.verify(password,Create_hash)

def create_access_token(user:dict,expiry:timedelta = None,refresh:bool=False):
     payload = {
          'user':user,
           'exp':datetime.now() + (expiry if expiry is not None else timedelta(minutes = ACCESS_TIME_MINUTES )),
           'jti':str(uuid.uuid4()),
           'refresh':refresh
     }
     return jwt.encode(payload=payload,key=Config.JWT_SECRET,algorithm=Config.JWT_ALGORITHM)

def create_refresh_access_token(user:dict,expiry:timedelta = None,refresh:bool=True):
       expiry = datetime.now() + (expiry or timedelta(days=7))
       payload = {
          'user':user,
          'exp':expiry,
          'jti':str(uuid.uuid4()),
          'refresh':refresh
     }
       return jwt.encode(payload=payload,key=Config.JWT_SECRET,algorithm=Config.JWT_ALGORITHM)
def decode_token(token:str):
     try:
         token_data = jwt.decode(jwt=token,algorithms=[Config.JWT_ALGORITHM],key=Config.JWT_SECRET)
         return token_data
     except jwt.PyJWTError as JTWERROR:
          logging.exception(JTWERROR)  
          return None  
     except Exception as e:
          logging.exception(e)
          return None
           
