from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

SECRET_KEY = "super-secret-key-change-in-real-project-2025"
serializer = URLSafeTimedSerializer(SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(pw_bytes)

def verify_password(plain: str, hashed: str) -> bool:
    pw_bytes = plain.encode("utf-8")[:72]
    return pwd_context.verify(pw_bytes, hashed)

def sign_data(data: dict) -> str:
    return serializer.dumps(data)

def unsign_data(token: str, max_age: int = 86400 * 30):
    try:
        return serializer.loads(token, max_age=max_age)
    except:
        return None