"""
services/spa_helpers.py — Utilidades compartidas para esperar que cargue una SPA.

Centraliza wait_for_spa() que antes estaba duplicada en:
  - services/screenshot_worker_impl.py
  - services/route_discovery_service.py
"""
from __future__ import annotations

from playwright.sync_api import Page


def wait_for_spa(page: Page) -> None:
    """
    Espera a que una SPA (React, Vue, Angular, etc.) haya terminado de renderizar.

    Estrategia combinada:
    1. Espera a que la red esté en reposo (networkidle).
    2. Espera a que el contenedor principal sea visible (#root, main, [role='main']).
    3. Pausa controlada para contenido asíncrono tardío.
    4. Elimina elementos dinámicos que distorsionan métricas (banners, loaders).
    """
    # 1. Red en reposo
    try:
        page.wait_for_load_state("networkidle", timeout=5_000)
    except Exception:
        pass

    # 2. Contenedor principal visible
    try:
        page.locator("#root, main, [role='main']").first.wait_for(
            state="visible", timeout=8_000
        )
    except Exception:
        pass

    # 3. Pausa para scripts diferidos
    page.wait_for_timeout(2_000)

    # 4. Limpiar elementos dinámicos que alteran las heurísticas de evaluación
    try:
        page.evaluate(
            """
            const remove = (selectors) =>
                selectors.forEach(s =>
                    document.querySelectorAll(s).forEach(el => el.remove())
                );
            remove([
                'iframe',
                '[id*="cookie"]',
                '[class*="cookie"]',
                '[role="dialog"]',
                '.spinner', '.loader', '.skeleton',
                '[aria-busy="true"]',
            ]);
            """
        )
    except Exception:
        pass
