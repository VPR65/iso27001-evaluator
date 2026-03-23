"""
Modulo de seguridad para ISO 27001 Evaluator

Este modulo proporciona:
- Proteccion CSRF para formularios
- Rate limiting para intentos de login
- Funciones de sanitizacion de entrada

Version: 1.1.2
Fecha: 2026-03-23
"""

import os
import time
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.responses import Response

# ==============================================================================
# CONFIGURACION DE SEGURIDAD
# ==============================================================================

# Clave secreta para tokens CSRF - debe cambiarse en produccion
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Configuracion de Rate Limiting
RATE_LIMIT_ATTEMPTS = 3  # Maximo de intentos
RATE_LIMIT_WINDOW = 300  # Ventana de tiempo en segundos (5 minutos)
RATE_LIMIT_LOCKOUT = 300  # Tiempo de bloqueo (5 minutos)

# Almacenamiento en memoria para rate limiting (en prod usar Redis)
_rate_limit_store: dict = {}


# ==============================================================================
# FUNCIONES CSRF
# ==============================================================================


def generate_csrf_token() -> str:
    """
    Genera un token CSRF unico.

    Returns:
        str: Token CSRF generado usando la clave secreta y timestamp
    """
    timestamp = str(int(time.time()))
    token_data = f"{SECRET_KEY}_{timestamp}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return f"{timestamp}_{token}"


def verify_csrf_token(token: str) -> bool:
    """
    Verifica si un token CSRF es valido.

    Args:
        token: Token CSRF a verificar

    Returns:
        bool: True si el token es valido, False en caso contrario
    """
    if not token or "_" not in token:
        return False

    try:
        timestamp_str, token_hash = token.split("_", 1)
        timestamp = int(timestamp_str)

        # Verificar que el token no sea muy viejo (24 horas)
        if time.time() - timestamp > 86400:
            return False

        # Verificar el hash
        expected_data = f"{SECRET_KEY}_{timestamp_str}"
        expected_hash = hashlib.sha256(expected_data.encode()).hexdigest()

        return token_hash == expected_hash
    except (ValueError, OverflowError):
        return False


# ==============================================================================
# RATE LIMITING
# ==============================================================================


def check_rate_limit(email: str) -> tuple[bool, Optional[int]]:
    """
    Verifica si el usuario puede intentar login.

    Implementa rate limiting para prevenir ataques de fuerza bruta.

    Args:
        email: Email del usuario que intenta login

    Returns:
        tuple: (puede_intentar, tiempo_restante_segundos)
    """
    now = time.time()
    key = f"login_{email.lower()}"

    # Obtener informacion previa
    if key in _rate_limit_store:
        attempts, blocked_until = _rate_limit_store[key]

        # Verificar si esta bloqueado
        if blocked_until and now < blocked_until:
            remaining = int(blocked_until - now)
            return False, remaining

        # Verificar si excedio intentos
        if attempts >= RATE_LIMIT_ATTEMPTS:
            # Bloquear al usuario
            blocked_until = now + RATE_LIMIT_LOCKOUT
            _rate_limit_store[key] = (attempts, blocked_until)
            return False, RATE_LIMIT_LOCKOUT

    return True, 0


def record_failed_attempt(email: str) -> None:
    """
    Registra un intento fallido de login.

    Args:
        email: Email del usuario que fallo el login
    """
    now = time.time()
    key = f"login_{email.lower()}"

    if key in _rate_limit_store:
        attempts, blocked_until = _rate_limit_store[key]

        # Si no esta bloqueado, incrementar intentos
        if not blocked_until or now >= blocked_until:
            _rate_limit_store[key] = (attempts + 1, None)
    else:
        _rate_limit_store[key] = (1, None)


def reset_rate_limit(email: str) -> None:
    """
    Resetea el contador de intentos fallidos despues de login exitoso.

    Args:
        email: Email del usuario que inicio sesion correctamente
    """
    key = f"login_{email.lower()}"
    if key in _rate_limit_store:
        del _rate_limit_store[key]


# ==============================================================================
# DEPENDENCIA FASTAPI PARA CSRF
# ==============================================================================


class CSRFProtection:
    """
    Dependencia FastAPI para proteger endpoints POST con CSRF.

    Usage:
        @app.post("/endpoint")
        def endpoint(request: Request, csrf: CSRFProtection = Depends()):
            ...
    """

    def __init__(self):
        self.token: Optional[str] = None

    def __call__(self, request: Request) -> "CSRFProtection":
        # Verificar que es un request valido
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Obtener token del header o form
            csrf_token = request.headers.get("X-CSRF-Token")

            if not csrf_token and hasattr(request, "form"):
                # Intentar obtener del form
                form_data = request.form()
                csrf_token = form_data.get("csrf_token")

            # Verificar el token
            if not csrf_token or not verify_csrf_token(csrf_token):
                raise HTTPException(
                    status_code=403, detail="Token CSRF invalido o faltante"
                )

        self.token = csrf_token
        return self


def get_csrf_token() -> str:
    """
    Genera un nuevo token CSRF para usar en formularios.

    Returns:
        str: Token CSRF valido
    """
    return generate_csrf_token()


# ==============================================================================
# HELPERS PARA RUTAS
# ==============================================================================


async def verify_csrf_from_request(request: Request) -> str:
    """
    Extrae y verifica el token CSRF de un request POST.
    Lanza HTTPException 403 si el token es invalido.

    Args:
        request: Request de FastAPI

    Returns:
        str: El token CSRF verificado

    Raises:
        HTTPException: Si el token falta o es invalido
    """
    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Token CSRF invalido o faltante")
    return csrf_token


# ==============================================================================
# SANITIZACION DE ENTRADAS
# ==============================================================================


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza entrada de usuario para prevenir XSS.

    Args:
        text: Texto a sanitizar
        max_length: Longitud maxima permitida

    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""

    # Limitar longitud
    text = text[:max_length]

    # Reemplazar caracteres potencialmente peligrosos
    dangerous_chars = {
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "&": "&amp;",
    }

    for char, replacement in dangerous_chars.items():
        text = text.replace(char, replacement)

    return text.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo para prevenir path traversal.

    Args:
        filename: Nombre de archivo a sanitizar

    Returns:
        str: Nombre de archivo seguro
    """
    # Eliminar rutas relativas
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")

    # Limitar longitud
    filename = filename[:255]

    return filename
