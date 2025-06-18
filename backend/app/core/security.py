from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verify JWT token and return subject"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def generate_password_reset_token(email: str) -> str:
    """Generate password reset token"""
    delta = timedelta(hours=24)  # Token expires in 24 hours
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": "strong" if len(errors) == 0 else "weak"
        }
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Basic input sanitization"""
        if not input_string:
            return ""
        
        # Remove potentially harmful characters
        dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\"]
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_rut(rut: str) -> bool:
        """Validate Chilean RUT"""
        if not rut:
            return False
        
        # Remove dots and hyphens
        clean_rut = rut.replace(".", "").replace("-", "")
        
        if len(clean_rut) < 8 or len(clean_rut) > 9:
            return False
        
        # Separate number and verification digit
        rut_number = clean_rut[:-1]
        verification_digit = clean_rut[-1].upper()
        
        # Calculate verification digit
        reversed_digits = rut_number[::-1]
        factors = [2, 3, 4, 5, 6, 7]
        sum_total = 0
        
        for i, digit in enumerate(reversed_digits):
            factor = factors[i % 6]
            sum_total += int(digit) * factor
        
        remainder = sum_total % 11
        calculated_digit = str(11 - remainder)
        
        if calculated_digit == "11":
            calculated_digit = "0"
        elif calculated_digit == "10":
            calculated_digit = "K"
        
        return verification_digit == calculated_digit