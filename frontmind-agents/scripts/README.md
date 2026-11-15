# Scripts del backend

Ejecútalos desde `frontmind-agents/` con el entorno virtual activo.

| Script | Uso |
| --- | --- |
| `check_deploy_files.py` | Verifica que `requirements.txt` esté en UTF-8. Lo usa el `Dockerfile` en el build. |
| `create_auth_state.py` | Abre un navegador para iniciar sesión a mano y guarda la sesión de Playwright (modo *storage state*). |
| `generate_synthetic_data.py` | Genera datos sintéticos de usuarios, proyectos y evaluaciones (`synthetic_frontmind_data.json`, no se versiona). |

## `experimentos/`

Scripts usados en los experimentos y pruebas documentados en `docs/pruebas/`. No forman parte de la API.

| Script | Uso |
| --- | --- |
| `test_url.py` | Captura una aplicación pública (prueba de humo). |
| `evaluate_iso.py` | Captura una URL y ejecuta la evaluación ISO/IEC 25010 sobre su HTML. |
| `test_macmillan_full.py` | Prueba manual del login de Macmillan. Requiere las variables `MACMILLAN_USER` y `MACMILLAN_PASSWORD`. |
| `framework_multiagente.py` | Prototipo inicial del framework multiagente con salida estructurada (requiere `google-genai`). |
