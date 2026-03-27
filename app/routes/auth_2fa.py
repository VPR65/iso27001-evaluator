"""
Endpoints para Autenticación en Dos Factores (2FA)
"""

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from app.models import User
from app.auth import get_current_user
from app.database import engine
from app.two_factor import (
    enable_2fa_for_user,
    verify_and_activate_2fa,
    disable_2fa_for_user,
    validate_2fa_code,
)
from app.security import verify_csrf_token

router = APIRouter(prefix="/auth/2fa", tags=["2fa"])


@router.get("/setup")
def setup_2fa(request: Request):
    """Mostrar pantalla para configurar 2FA"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        # Generar secreto y QR
        try:
            secret, qr_base64 = enable_2fa_for_user(user.id, session)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al generar 2FA: {str(e)}"
            )

        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Configurar 2FA</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        </head>
        <body class="container">
            <h1>🔐 Configurar Autenticación en Dos Factores</h1>
            
            <ol>
                <li>Instalar una app de autenticación en tu celular:
                    <ul>
                        <li>Google Authenticator: <a href="https://support.google.com/accounts/answer/1066447">Android/iOS</a></li>
                        <li>Authy: <a href="https://authy.com/">Sitio web</a></li>
                        <li>Microsoft Authenticator: <a href="https://www.microsoft.com/es-es/account/authenticator">Sitio web</a></li>
                    </ul>
                </li>
                <li>Escanea el código QR con tu app</li>
                <li>Ingresa el código de 6 dígitos que muestra la app</li>
                <li>Hacé clic en "Verificar y Activar"</li>
            </ol>
            
            <div style="text-align: center; margin: 2rem 0;">
                <img src="{qr_base64}" alt="QR Code" style="border: 2px solid #000; padding: 1rem;">
                <p><strong>Secret (para ingreso manual):</strong> <code>{secret}</code></p>
            </div>
            
            <form method="post" action="/auth/2fa/verify">
                <input type="hidden" name="csrf_token" value="{{{{ csrf_token }}}}" />
                <label>
                    Código de verificación (6 dígitos)
                    <input type="text" name="code" pattern="[0-9]{{6}}" maxlength="6" required placeholder="Ej: 123456">
                </label>
                <button type="submit" class="btn btn-primary">Verificar y Activar</button>
            </form>
            
            <a href="/dashboard" class="btn btn-outline">Cancelar</a>
        </body>
        </html>
        """)


@router.post("/verify")
async def verify_2fa_setup(request: Request, code: str = Form(...)):
    """Verificar código y activar 2FA"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    # Validar CSRF
    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF inválido")

    with Session(engine) as session:
        if verify_and_activate_2fa(user.id, code, session):
            # 2FA activado exitosamente
            return RedirectResponse("/auth/2fa/success", status_code=303)
        else:
            # Código inválido
            return RedirectResponse("/auth/2fa/setup?error=1", status_code=303)


@router.get("/success")
def success_2fa(request: Request):
    """Pantalla de éxito"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>2FA Activado</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    </head>
    <body class="container">
        <h1>✅ 2FA Activado Exitosamente</h1>
        <p>Tu autenticación en dos factores ha sido activada.</p>
        <p>Ahora, cada vez que inicies sesión, deberás ingresar un código de 6 dígitos de tu app autenticadora.</p>
        <a href="/dashboard" class="btn btn-primary">Ir al Dashboard</a>
    </body>
    </html>
    """)


@router.post("/disable")
async def disable_2fa(request: Request):
    """Deshabilitar 2FA"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF inválido")

    with Session(engine) as session:
        if disable_2fa_for_user(user.id, session):
            return RedirectResponse("/dashboard?msg=2fa_disabled", status_code=303)
        else:
            return RedirectResponse("/dashboard?msg=2fa_disable_error", status_code=303)


@router.get("/status")
def get_2fa_status(request: Request):
    """Obtener estado actual de 2FA del usuario"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    return {
        "enabled": user.two_factor_enabled,
        "verified": user.two_factor_verified,
        "has_secret": bool(user.two_factor_secret),
    }
