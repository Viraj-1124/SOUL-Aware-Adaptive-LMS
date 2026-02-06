from datetime import datetime, timedelta
from jose import jwt,JWTError

SECRET_KEY = "SUPER SECRET KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 60

def create_access_token(user_id: int, role:str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None