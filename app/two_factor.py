"""
Servicio de Autenticación en Dos Factores (2FA)
Usa TOTP (Time-based One-Time Password) compatible con Google Authenticator, Authy, etc.
"""

import pyotp
import qrcode
import base64
import io
from typing import Optional, Tuple
from sqlmodel import Session
from app.models import User


def generate_totp_secret() -> str:
    """Generar un nuevo secreto TOTP"""
    return pyotp.random_base32()


def get_totp_uri(email: str, secret: str) -> str:
    """
    Generar URI para QR de 2FA
    Formato: otpauth://totp/ISSUER:email?secret=SECRET&issuer=ISSUER
    """
    issuer = "ISO27001-Evaluator"
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code(uri: str) -> str:
    """
    Generar código QR en base64 para mostrar en el frontend
    Returns: Base64 del QR en formato PNG
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar en buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Convertir a base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"


def verify_totp(secret: str, code: str) -> bool:
    """
    Verificar un código TOTP
    Returns: True si es válido, False si no
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # 1 ventana de tolerancia (30 seg)


def enable_2fa_for_user(user_id: str, session: Session) -> Tuple[str, str]:
    """
    Habilitar 2FA para un usuario
    Returns: (secreto, QR_base64)
    """
    user = session.get(User, user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    # Generar nuevo secreto
    secret = generate_totp_secret()
    user.two_factor_secret = secret
    user.two_factor_enabled = False  # Aún no verificado
    session.add(user)
    session.commit()

    # Generar URI y QR
    uri = get_totp_uri(user.email, secret)
    qr_base64 = generate_qr_code(uri)

    return secret, qr_base64


def verify_and_activate_2fa(user_id: str, code: str, session: Session) -> bool:
    """
    Verificar código y activar 2FA
    Returns: True si éxito, False si falla
    """
    user = session.get(User, user_id)
    if not user or not user.two_factor_secret:
        return False

    # Verificar código
    if verify_totp(user.two_factor_secret, code):
        user.two_factor_enabled = True
        user.two_factor_verified = True
        session.add(user)
        session.commit()
        return True

    return False


def disable_2fa_for_user(user_id: str, session: Session) -> bool:
    """
    Deshabilitar 2FA para un usuario
    """
    user = session.get(User, user_id)
    if not user:
        return False

    user.two_factor_enabled = False
    user.two_factor_verified = False
    user.two_factor_secret = None
    session.add(user)
    session.commit()
    return True


def validate_2fa_code(user: User, code: str) -> bool:
    """
    Validar código 2FA para login
    """
    if not user.two_factor_enabled or not user.two_factor_secret:
        return True  # No requiere 2FA

    return verify_totp(user.two_factor_secret, code)
