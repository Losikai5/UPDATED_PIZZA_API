from passlib.context  import CryptContext
import jwt
from datetime import timedelta,datetime, timezone
import uuid
import logging
from src.config import Config
from itsdangerous import URLSafeTimedSerializer

pwd_hash = CryptContext(schemes=["bcrypt"],deprecated = "auto")
ACCESS_TIME_MINUTES = 60
serializer = URLSafeTimedSerializer(Config.JWT_SECRET,salt="email-confirmation-salt")


def create_hash(password: str):
    return pwd_hash.hash(password)

def verify_hash(password: str, hashed_password: str):
    return pwd_hash.verify(password, hashed_password)

def create_access_token(user:dict,expiry:timedelta = None,refresh:bool=False):
     payload = {
          'user':user,
           'exp':datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(minutes = ACCESS_TIME_MINUTES )),
           'jti':str(uuid.uuid4()),
           'refresh':refresh
     }
     return jwt.encode(payload=payload,key=Config.JWT_SECRET,algorithm=Config.JWT_ALGORITHM)

def create_refresh_access_token(user:dict,expiry:timedelta = None,refresh:bool=True):
       expiry = datetime.now(timezone.utc) + (expiry or timedelta(days=7))
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
     
def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token
def decode_url_safe_token(token: str) -> dict:
     try:
          data = serializer.loads(token, max_age=3600)  # Token valid for 1 hour
          return data
     except Exception as e:
          logging.exception(e)
          return None
     
