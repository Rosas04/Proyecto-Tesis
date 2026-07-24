import io
import zipfile
from locust import HttpUser, task, between, tag

class FrontMindLoadTest(HttpUser):
    # Tiempo de espera simulado entre acciones de usuario (1 a 3 segundos)
    wait_time = between(1, 3)

    def _create_dummy_zip(self):
        """Crea un archivo ZIP en memoria con un HTML básico para la prueba de carga."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.html', '<html><body><h1>Load Test</h1></body></html>')
            zf.writestr('style.css', 'body { background: #000; color: #fff; }')
        buffer.seek(0)
        return buffer

    @tag('cp-car-01')
    @task(5)
    def test_cp_car_01_history(self):
        """CP-CAR-01: Concurrencia de Lectura y Autenticación (Supabase/DB)."""
        self.client.get("/history?user_id=load_test_user", name="CP-CAR-01: GET /history")

    @tag('cp-car-02')
    @task(2)
    def test_cp_car_02_upload_zip(self):
        """CP-CAR-02: Subida y Desempaquetado Simultáneo de ZIPs (I/O Stress)."""
        zip_buffer = self._create_dummy_zip()
        files = {'file': ('load_test.zip', zip_buffer, 'application/zip')}
        self.client.post("/upload/zip", files=files, name="CP-CAR-02: POST /upload/zip")

    @tag('cp-car-03')
    @task(1)
    def test_cp_car_03_capture_playwright(self):
        """CP-CAR-03: Múltiples Agentes Playwright Simultáneos (Memory Stress)."""
        payload = {
            "url": "https://example.com",
            "max_pages": 1
        }
        self.client.post("/capture/url", json=payload, name="CP-CAR-03: POST /capture/url")
