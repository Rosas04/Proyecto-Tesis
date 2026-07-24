from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import re

from playwright.sync_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError


class AuthenticationError(RuntimeError):
    """Error controlado durante la autenticación automatizada."""


def normalize_auth_config(auth: dict[str, Any] | None) -> dict[str, Any]:
    if not auth:
        return {"mode": "none"}

    mode = auth.get("mode", "none")
    if mode == "none" and auth.get("username") and auth.get("password"):
        mode = "form"

    return {
        "mode": mode,
        "login_url": auth.get("login_url"),
        "username": auth.get("username"),
        "password": auth.get("password"),
        "username_selector": auth.get("username_selector"),
        "password_selector": auth.get("password_selector"),
        "submit_selector": auth.get("submit_selector"),
        "success_url_pattern": auth.get("success_url_pattern"),
        "success_selector": auth.get("success_selector"),
        "storage_state_path": auth.get("storage_state_path"),
    }


def validate_form_auth(auth: dict[str, Any]) -> None:
    # Only require username and password; everything else can be auto-detected
    required = {
        "username": auth.get("username"),
        "password": auth.get("password"),
    }

    missing = [name for name, value in required.items() if not value]

    if missing:
        raise AuthenticationError(
            "Faltan datos para autenticación: " + ", ".join(missing)
        )


def perform_form_login(
    page: Page,
    auth: dict[str, Any],
    url: str,
    timeout_ms: int = 60_000,
) -> None:
    """
    Inicia sesión mediante un formulario HTML. Si no se proveen selectores, 
    utiliza heurísticas y Playwright locator para encontrarlos automáticamente.
    """
    validate_form_auth(auth)

    # Si no nos dan login_url, navegamos a la URL inicial y dejamos que nos redirija
    login_url = auth.get("login_url") or url

    try:
        page.goto(
            login_url,
            wait_until="domcontentloaded",
            timeout=timeout_ms,
        )

        # Darle tiempo a la página por si hay alguna redirección (ej. a /login)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            pass

        # === NUEVO: Intentar cerrar banners de cookies automáticamente ===
        try:
            # Buscar botones comunes de cookies
            cookie_btn = page.locator(
                'button:has-text("Accept all cookies"), '
                'button:has-text("Aceptar todas"), '
                'button:has-text("Aceptar cookies"), '
                'button:has-text("Accept Cookies"), '
                '[aria-label*="cookie" i], '
                'button[id*="cookie" i], '
                'button[class*="cookie" i]'
            ).first
            
            if cookie_btn.count() > 0 and cookie_btn.is_visible():
                cookie_btn.click(timeout=3000, force=True)
                print("[DEBUG auth] Cookie banner dismissed.", file=sys.stderr)
        except Exception as e:
            pass
        # ==============================================================

        def find_username_field():
            if auth.get("username_selector"):
                return page.locator(auth["username_selector"]).first
            loc1 = page.get_by_placeholder(re.compile(r"correo|email|usuario|username|id", re.IGNORECASE))
            loc2 = page.get_by_label(re.compile(r"correo|email|usuario|username|id", re.IGNORECASE))
            loc3 = page.locator("input[type='email' i], input[type='text' i], input[name*='email' i], input[name*='user' i], input[id*='user' i]")
            return loc1.or_(loc2).or_(loc3).first

        username_field = find_username_field()
        
        # Si no encontramos el input, tal vez estamos en una página puente (ej. Macmillan)
        try:
            username_field.wait_for(state="attached", timeout=5000)
        except PlaywrightTimeoutError:
            # Intentar buscar un enlace genérico de "Log in" y darle click
            login_link = page.get_by_role("link", name=re.compile(r"iniciar sesión|login|sign in|acceder", re.IGNORECASE)).or_(
                page.locator("a[href*='login' i], a[href*='signin' i], button:has-text('Log in')")
            ).first
            
            # Usar un bloque try para verificar si es visible o si lo podemos clickear
            try:
                if login_link.is_visible():
                    login_link.click(force=True, timeout=5000)
                    page.wait_for_load_state("networkidle", timeout=8000)
                    page.wait_for_timeout(2000)
                    username_field = find_username_field()
                else:
                    # Alternativa: redirigir forzosamente si encontramos un href
                    href = login_link.get_attribute("href", timeout=2000)
                    if href:
                        page.goto(href if href.startswith('http') else page.url.rstrip('/') + '/' + href.lstrip('/'))
                        page.wait_for_load_state("networkidle", timeout=8000)
                        username_field = find_username_field()
            except Exception as e:
                print(f"[DEBUG auth] Error clicking login link: {e}", file=sys.stderr)
                pass

        # Usar force=True para ignorar banners de cookies gigantes que interceptan clics
        username_field.fill(auth["username"], force=True)
        page.wait_for_timeout(500)

        # 2. Buscar campo de Password
        def get_password_field():
            if auth.get("password_selector"):
                return page.locator(auth["password_selector"]).first
            loc1 = page.get_by_placeholder(re.compile(r"contraseña|password|clave|pass", re.IGNORECASE))
            loc2 = page.get_by_label(re.compile(r"contraseña|password|clave|pass", re.IGNORECASE))
            loc3 = page.locator("input[type='password' i], input[name*='password' i], input[name*='clave' i], input[name*='pass' i], input[id*='pass' i], input[id*='clave' i]")
            return loc1.or_(loc2).or_(loc3).first

        password_field = get_password_field()

        try:
            password_field.wait_for(state="attached", timeout=4000)
        except PlaywrightTimeoutError:
            # Posible login de 2 pasos. Intentar presionar Enter en el campo de usuario.
            try:
                username_field.press("Enter")
                page.wait_for_timeout(1500)
            except Exception:
                pass

            # Si presionar Enter no funcionó, buscar un botón explícito
            try:
                if not password_field.is_visible():
                    next_btn = page.get_by_role("button", name=re.compile(r"siguiente|next|continuar|continue", re.IGNORECASE)).or_(page.locator("button[type='submit'], input[type='submit']")).first
                    if next_btn.is_visible():
                        next_btn.click(force=True, timeout=3000)
                        page.wait_for_timeout(1500)
            except Exception:
                pass

        try:
            password_field.wait_for(state="attached", timeout=8000)
            password_field.fill(auth["password"], force=True, timeout=5000)
        except PlaywrightTimeoutError:
            raise AuthenticationError(
                "No se pudo encontrar el campo de contraseña. Si el login tiene múltiples pasos complejos o reCAPTCHA, puede fallar el heurístico automático."
            )

        # 3. Enviar el formulario (Submit)
        try:
            # Es mucho más seguro presionar Enter directamente en el campo de contraseña
            password_field.press("Enter")
            page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # Si la URL no cambió o hubo un problema, intentamos buscar y clickear el botón explícitamente
        try:
            if auth.get("submit_selector"):
                submit_btn = page.locator(auth["submit_selector"]).first
                if submit_btn.is_visible():
                    submit_btn.click(force=True, timeout=3000)
            else:
                loc1 = page.get_by_role("button", name=re.compile(r"ingresar|iniciar sesión|login|sign in|acceder|continuar|entrar", re.IGNORECASE))
                loc2 = page.locator("button[type='submit'], input[type='submit'], button")
                submit_btn = loc1.or_(loc2).first
                if submit_btn.is_visible():
                    submit_btn.click(force=True, timeout=3000)
        except Exception:
            pass

        # 4. Esperar a que pase el login (Redirección o cambio de DOM)
        success_selector = auth.get("success_selector")
        success_url_pattern = auth.get("success_url_pattern")

        page.screenshot(path="debug_before_wait.png")

        if success_selector:
            try:
                page.locator(success_selector).first.wait_for(
                    state="visible", timeout=15000
                )
            except PlaywrightTimeoutError:
                raise AuthenticationError(
                    f"No se encontró el selector de éxito '{success_selector}' "
                    "después del inicio de sesión."
                )
        elif success_url_pattern:
            try:
                page.wait_for_url(
                    re.compile(success_url_pattern),
                    timeout=15000,
                )
            except PlaywrightTimeoutError:
                pass
        else:
            # Esperar a que la URL cambie
            initial_url = page.url
            print(f"[DEBUG auth] Waiting for URL to change from {initial_url}...", file=sys.stderr)
            try:
                # Wait for navigation to something that is not the initial login page
                # and hopefully not an intermediate SSO redirect if possible, by waiting longer
                page.wait_for_url(lambda u: u != initial_url and "login" not in u.lower() and "sso" not in u.lower(), timeout=15000)
                print(f"[DEBUG auth] URL changed to {page.url}!", file=sys.stderr)
            except PlaywrightTimeoutError:
                print(f"[DEBUG auth] Timeout waiting for URL change. Current URL is {page.url}", file=sys.stderr)

            try:
                page.wait_for_load_state("networkidle", timeout=8000)
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                pass
            print(f"[DEBUG auth] Final URL before return: {page.url}", file=sys.stderr)

        page.wait_for_timeout(2_000)
        page.screenshot(path="debug_after_wait.png")

    except PlaywrightTimeoutError as exc:
        raise AuthenticationError(
            "Tiempo de espera agotado durante la autenticación. Es posible que los heurísticos no hayan encontrado los campos en esta página específica."
        ) from exc
    except Exception as exc:
        raise AuthenticationError(
            f"Error durante la autenticación: {exc}"
        ) from exc


def save_storage_state(
    context: BrowserContext,
    destination: str,
) -> str:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)

    context.storage_state(path=str(path))

    return str(path)
