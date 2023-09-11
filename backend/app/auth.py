import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import json
from fastapi import HTTPException

class Auther:
    def __init__(self):
        self.password_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto"
        )
        self.JWT_EXPIRY_MINUTES = 7 * 60 * 24 # 7 days

    def get_hashed_password(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify_password(
        self, 
        password: str, 
        hashed_password: str
    ) -> bool:
        return self.password_context.verify(password, hashed_password)

    def create_jwt(
        self,
        subject: str,
        secret_key: str,
        expires_delta: int = None
    ) -> str:
        if expires_delta is not None:
            expiry = datetime.utcnow() + timedelta(minutes=expires_delta)
        else:
            expiry = datetime.utcnow() + timedelta(minutes=self.JWT_EXPIRY_MINUTES) # in seconds since unix epoch
        payload = { "exp": expiry, "sub": subject } 
        token = jwt.encode(payload=payload, key=secret_key) # Uses HS256 by default
        return token

    def decode_jwt(
        self,
        token,
        secret
    ) -> str:
        return jwt.decode(token, key=secret, algorithms=['HS256',])

    def get_new_jwt_secret(self):
        return secrets.token_urlsafe(64)

    def get_user_from_jwt(
        self,
        authorization: str,
    ) -> str:
        token = authorization.split()[1]
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload['sub']

    def authorize_user(
        self,
        authorization: str,
        secret_key: str
    ) -> str:
        token = authorization.split()[1]
        try:
            payload = self.decode_jwt(
                token, 
                secret_key
            )
            # TODO this should be checking both expiry and id of payload
            # now = datetime.utcnow().timestamp()
            return True
        except Exception as e:
            print(e)
            return False
