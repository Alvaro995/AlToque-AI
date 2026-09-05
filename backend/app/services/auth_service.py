"""Servicio de autenticación, hash de contraseñas y emisión de tokens JWT."""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User, PatientProfile
from app.schemas.user import UserCreate


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña en texto plano contra hash seguro."""
    try:
        import bcrypt
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
    except ImportError:
        pass

    # PBKDF2-HMAC-SHA256 fallback
    if hashed_password.startswith("$pbkdf2$"):
        parts = hashed_password.split("$")
        if len(parts) == 4:
            salt = bytes.fromhex(parts[2])
            expected = parts[3]
            computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000).hex()
            return hmac.compare_digest(computed, expected)
    return False


def get_password_hash(password: str) -> str:
    """Genera hash seguro de contraseña usando PBKDF2 o bcrypt."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except ImportError:
        import os
        salt = os.urandom(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()
        return f"$pbkdf2${salt.hex()}${h}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera token de acceso JWT firmado con expiración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": int(expire.timestamp())})

    try:
        from jose import jwt
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except ImportError:
        pass

    # Pure standard library JWT generation
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode("utf-8")).decode("utf-8").rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode("utf-8")).decode("utf-8").rstrip("=")
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{header_b64}.{payload_b64}.{sig_b64}"


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Obtiene usuario por dirección de correo electrónico."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Obtiene usuario por identificador único."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Valida credenciales y retorna usuario autenticado."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Registra un nuevo usuario e inicializa perfil si es paciente."""
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hashed_password,
        role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role),
        full_name=user_in.full_name,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    if user.role == "patient":
        profile = PatientProfile(
            user_id=user.id,
            profile_completeness_pct=10.0,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(user)
    return user
