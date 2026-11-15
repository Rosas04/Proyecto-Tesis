import json
import random
from datetime import datetime, timedelta
import uuid

def generate_synthetic_data():
    users = []
    projects = []
    interfaces = []
    evaluations = []
    reports = []
    
    # 1. Simular Usuarios
    for i in range(5):
        user_id = str(uuid.uuid4())
        users.append({
            "user_id": user_id,
            "email": f"tester{i+1}@frontmind.ai",
            "name": f"Usuario de Pruebas {i+1}",
            "role": "tester"
        })
        
        # 2. Simular Proyectos por Usuario
        for p in range(random.randint(1, 3)):
            project_id = str(uuid.uuid4())
            project_name = random.choice(["E-commerce Frontend", "Dashboard Admin", "Landing Page Corporativa", "Sistema Académico", "Portal de Noticias"])
            projects.append({
                "project_id": project_id,
                "user_id": user_id,
                "name": project_name,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
            
            # 3. Simular Interfaces por Proyecto
            num_interfaces = random.randint(2, 6)
            project_global_score = 0
            
            for iface in range(num_interfaces):
                interface_id = str(uuid.uuid4())
                iface_name = f"{project_name} - Vista {iface+1}"
                
                # 4. Simular Capturas
                captures = [
                    {"device": "desktop", "public_url": f"/captures/mock_{interface_id}_desktop.png"},
                    {"device": "tablet", "public_url": f"/captures/mock_{interface_id}_tablet.png"},
                    {"device": "mobile", "public_url": f"/captures/mock_{interface_id}_mobile.png"}
                ]
                
                interfaces.append({
                    "interface_id": interface_id,
                    "project_id": project_id,
                    "name": iface_name,
                    "route": f"/{iface_name.lower().replace(' ', '-')}",
                    "capture_time_seconds": round(random.uniform(1.5, 4.5), 2),
                    "captures": captures
                })
                
                # 5. Simular Evaluaciones ISO 25010
                global_score = random.randint(65, 98)
                project_global_score += global_score
                
                level = "Excelente" if global_score >= 90 else "Alto" if global_score >= 80 else "Medio" if global_score >= 60 else "Bajo"
                
                evaluations.append({
                    "evaluation_id": str(uuid.uuid4()),
                    "interface_id": interface_id,
                    "global_score": global_score,
                    "quality_level": level,
                    "scores": {
                        "adecuacion_funcional": random.randint(70, 100),
                        "eficiencia_desempeno": random.randint(60, 100),
                        "usabilidad": random.randint(70, 100),
                        "mantenibilidad": random.randint(50, 95)
                    },
                    "findings": [
                        {"severity": "Media", "dimension": "Usabilidad", "finding": "Contraste bajo", "recommendation": "Aumentar contraste a 4.5:1"}
                    ],
                    "total_findings": random.randint(1, 5)
                })
                
            # 6. Simular Reporte Consolidado del Proyecto
            avg_score = project_global_score // num_interfaces
            report_level = "Excelente" if avg_score >= 90 else "Alto" if avg_score >= 80 else "Medio" if avg_score >= 60 else "Bajo"
            
            reports.append({
                "report_id": str(uuid.uuid4()),
                "project_id": project_id,
                "total_interfaces": num_interfaces,
                "average_score": avg_score,
                "overall_quality_level": report_level,
                "generated_at": datetime.now().isoformat()
            })
            
    database = {
        "users": users,
        "projects": projects,
        "interfaces": interfaces,
        "evaluations": evaluations,
        "reports": reports
    }
    
    with open("synthetic_frontmind_data.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
        
    print("Datos sintéticos generados en 'synthetic_frontmind_data.json'")

if __name__ == "__main__":
    generate_synthetic_data()
