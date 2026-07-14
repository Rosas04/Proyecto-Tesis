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
            
        def find_username_field():
            if auth.get("username_selector"):
                return page.locator(auth["username_selector"]).first
            loc1 = page.get_by_placeholder(re.compile(r"correo|email|usuario|username", re.IGNORECASE))
            loc2 = page.get_by_label(re.compile(r"correo|email|usuario|username", re.IGNORECASE))
            loc3 = page.locator("input[type='email'], input[name='email'], input[name='username'], input[type='text']")
            return loc1.or_(loc2).or_(loc3).first

        username_field = find_username_field()
        
        # Si no encontramos el input, tal vez estamos en una página puente (ej. Macmillan)
        try:
            username_field.wait_for(state="attached", timeout=5000)
        except PlaywrightTimeoutError:
            # Intentar buscar un enlace genérico de "Log in" y darle click
            login_link = page.get_by_role("link", name=re.compile(r"iniciar sesión|login|sign in|acceder", re.IGNORECASE)).or_(page.locator("a[href*='login'], a[href*='signin']")).first
            if login_link.count() > 0:
                try:
                    login_link.click(force=True, timeout=5000)
                    page.wait_for_load_state("networkidle", timeout=8000)
                    username_field = find_username_field()
                except Exception:
                    pass

        # Usar force=True para ignorar banners de cookies gigantes que interceptan clics
        username_field.fill(auth["username"], force=True)

        # 2. Buscar campo de Password
        if auth.get("password_selector"):
            password_field = page.locator(auth["password_selector"]).first
        else:
            loc1 = page.get_by_placeholder(re.compile(r"contraseña|password|clave", re.IGNORECASE))
            loc2 = page.get_by_label(re.compile(r"contraseña|password|clave", re.IGNORECASE))
            loc3 = page.locator("input[type='password'], input[name='password']")
            password_field = loc1.or_(loc2).or_(loc3).first

        password_field.fill(auth["password"], force=True)

        # 3. Buscar y clickear Submit
        if auth.get("submit_selector"):
            submit_btn = page.locator(auth["submit_selector"]).first
        else:
            loc1 = page.get_by_role("button", name=re.compile(r"ingresar|iniciar sesión|login|sign in|acceder|continuar|entrar", re.IGNORECASE))
            loc2 = page.locator("button[type='submit'], input[type='submit'], button")
            submit_btn = loc1.or_(loc2).first
        
        submit_btn.click(force=True)

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
                page.wait_for_url(lambda u: u != initial_url, timeout=12000)
                print(f"[DEBUG auth] URL changed to {page.url}!", file=sys.stderr)
            except PlaywrightTimeoutError:
                print(f"[DEBUG auth] Timeout waiting for URL change. Current URL is {page.url}", file=sys.stderr)

            try:
                page.wait_for_load_state("networkidle", timeout=5000)
                page.wait_for_timeout(2000)
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
