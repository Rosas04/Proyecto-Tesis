from locust import HttpUser, task, between

class FrontMindUser(HttpUser):
    # Tiempo de espera simulado entre acciones de usuario (1 a 3 segundos)
    wait_time = between(1, 3)

    @task(4)
    def health_check(self):
        """Simula una comprobación de estado básica o polling del frontend."""
        self.client.get("/", name="GET / (Health)")

    @task(3)
    def get_history(self):
        """Simula a un usuario cargando la vista de Historial."""
        self.client.get("/history?user_id=test_user_123", name="GET /history")

    @task(2)
    def evaluate_iso_light(self):
        """Simula el procesamiento intensivo en CPU de una evaluación ISO."""
        payload = {
            "html": "<html><head><title>Test</title></head><body><main><h1>Hello World</h1><p>Testing</p></main></body></html>",
            "user_id": "test_user_123"
        }
        self.client.post("/evaluate/iso", json=payload, name="POST /evaluate/iso")

    @task(1)
    def generate_report(self):
        """Simula la generación de un reporte final."""
        payload = {
            "evaluation": {
                "global_score": 85,
                "quality_level": "Alto",
                "scores": {"usabilidad": 90, "rendimiento": 80},
                "findings": [{"severity": "Media", "dimension": "Usabilidad"}],
                "total_findings": 1
            },
            "user_id": "test_user_123"
        }
        self.client.post("/report/generate", json=payload, name="POST /report/generate")
