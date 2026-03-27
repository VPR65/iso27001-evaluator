"""
Servicio de Encriptación de Evidencias - Sprint 3.3
Usa Fernet (symmetric encryption) para encriptar archivos subidos
"""

from cryptography.fernet import Fernet
from pathlib import Path
import base64
import os

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", None)


def get_or_create_key() -> str:
    """Obtener clave de encriptación o generar una nueva"""
    if ENCRYPTION_KEY:
        return ENCRYPTION_KEY

    # Si no hay key, generar una nueva (solo para desarrollo)
    key = Fernet.generate_key()
    return key.decode()


def encrypt_file(filepath: str, key: str = None) -> str:
    """
    Encriptar archivo y guardar con extensión .enc
    Returns: ruta del archivo encriptado
    """
    if not key:
        key = get_or_create_key()

    f = Fernet(key.encode())

    # Leer archivo original
    with open(filepath, "rb") as file:
        file_data = file.read()

    # Encriptar
    encrypted_data = f.encrypt(file_data)

    # Guardar archivo encriptado
    encrypted_path = filepath + ".enc"
    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)

    # Eliminar archivo original (opcional, por seguridad)
    Path(filepath).unlink()

    return encrypted_path


def decrypt_file(encrypted_filepath: str, key: str = None) -> str:
    """
    Desencriptar archivo y guardar sin extensión .enc
    Returns: ruta del archivo desencriptado
    """
    if not key:
        key = get_or_create_key()

    f = Fernet(key.encode())

    # Leer archivo encriptado
    with open(encrypted_filepath, "rb") as file:
        encrypted_data = file.read()

    # Desencriptar
    decrypted_data = f.decrypt(encrypted_data)

    # Guardar archivo desencriptado (quitar .enc)
    decrypted_path = encrypted_filepath[:-4]  # Quitar '.enc'
    with open(decrypted_path, "wb") as file:
        file.write(decrypted_data)

    return decrypted_path


def encrypt_content(content: bytes, key: str = None) -> bytes:
    """Encriptar contenido en memoria"""
    if not key:
        key = get_or_create_key()

    f = Fernet(key.encode())
    return f.encrypt(content)


def decrypt_content(encrypted_content: bytes, key: str = None) -> bytes:
    """Desencriptar contenido en memoria"""
    if not key:
        key = get_or_create_key()

    f = Fernet(key.encode())
    return f.decrypt(encrypted_content)


def is_encrypted(filepath: str) -> bool:
    """Verificar si un archivo está encriptado"""
    return filepath.endswith(".enc")
