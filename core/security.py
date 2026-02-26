from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.user_model import User
from core.logger import setup_logger

logger = setup_logger("security")

# =========================
# CONFIG
# =========================

SECRET_KEY = "SECRET123"  # ganti di production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# PASSWORD
# =========================

def get_password_hash(password: str) -> str:
    hashed = pwd_context.hash(password)
    logger.debug(f"✅ Password hashed successfully")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_valid = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"🔐 Password verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    return is_valid


# =========================
# TOKEN
# =========================

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"🎫 Token created: {encoded_jwt[:30]}... (expires in {expires_delta} min)")
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ Error creating token: {str(e)}")
        raise


def decode_token(token: str):
    """
    Decode dan validasi JWT token
    Return: payload dict jika valid, None jika invalid
    """
    try:
        if not token:
            logger.warning(f"⚠️  Empty token received")
            return None
            
        logger.debug(f"🔍 Decoding token: {token[:30]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"✅ Token decoded successfully: {payload}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning(f"⚠️  Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️  Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error decoding token: {str(e)}")
        return None


def decode_token(token: str):
    """
    Decode dan validasi JWT token
    Return: payload dict jika valid, None jika invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("⚠️  Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"⚠️  Invalid token: {str(e)}")
        return None
    except Exception as e:
        print(f"⚠️  Decode error: {str(e)}")
        return None


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    return user


# =========================
# ROLE CHECKING
# =========================

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


def require_seller(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["seller", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )
    return current_user# TOKEN
# =========================

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )

    try:
        logger.debug(f"🔐 get_current_user: Validating token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            logger.warning(f"⚠️  No email in token payload")
            raise credentials_exception

    except JWTError as e:
        logger.warning(f"⚠️  JWTError: {str(e)}")
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        logger.warning(f"⚠️  User not found: {email}")
        raise credentials_exception

    logger.info(f"✅ User authenticated: {user.email}")
    return user


# =========================
# ROLE CHECKING
# =========================

def require_admin(current_user: User = Depends(get_current_user)):
    logger.debug(f"🔐 Checking admin role for: {current_user.email}")
    if current_user.role != "admin":
        logger.warning(f"❌ Access denied - not admin: {current_user.email}")
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    logger.info(f"✅ Admin access granted: {current_user.email}")
    return current_user


def require_seller(current_user: User = Depends(get_current_user)):
    logger.debug(f"🔐 Checking seller role for: {current_user.email}")
    if current_user.role not in ["seller", "admin"]:
        logger.warning(f"❌ Access denied - not seller: {current_user.email}")
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )
    logger.info(f"✅ Seller access granted: {current_user.email}")
    return current_user
    return current_user
