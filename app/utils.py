from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

SECRET_KEY = "super-secret-key-change-in-real-project"
serializer = URLSafeTimedSerializer(SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def sign_data(data: dict) -> str:
    return serializer.dumps(data)

def unsign_data(token: str, max_age: int = 86400 * 30):
    try:
        return serializer.loads(token, max_age=max_age)
    except:
        return None