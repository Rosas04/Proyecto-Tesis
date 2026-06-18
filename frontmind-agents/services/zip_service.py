import zipfile
from pathlib import Path
import shutil


ALLOWED_EXTENSIONS = [
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".tsx",
    ".ts",
]


def extract_zip_project(zip_file_path: str):
    extract_dir = Path("extracted_projects")

    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    extract_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        return {
            "status": "error",
            "message": "El archivo enviado no es un ZIP válido.",
            "total_files": 0,
            "files": [],
            "combined_code": "",
        }

    extracted_files = []
    combined_code = ""

    for file_path in extract_dir.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if "node_modules" in str(file_path):
            continue

        if "dist" in str(file_path):
            continue

        if "venv" in str(file_path):
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            extracted_files.append(
                {
                    "file_name": file_path.name,
                    "path": str(file_path),
                    "extension": file_path.suffix.lower(),
                    "size": len(content),
                }
            )

            combined_code += f"\n\n<!-- FILE: {file_path} -->\n"
            combined_code += content

        except Exception:
            pass

    return {
        "status": "extracted",
        "message": "Proyecto ZIP extraído correctamente.",
        "total_files": len(extracted_files),
        "files": extracted_files,
        "combined_code": combined_code,
    }