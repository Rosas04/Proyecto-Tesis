from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.capture_agent import CaptureAgent
from agents.html_replication_agent import HtmlReplicationAgent
from agents.iso_evaluation_agent import ISOEvaluationAgent
from agents.report_agent import ReportAgent
from services.zip_service import extract_zip_project


class UrlRequest(BaseModel):
    url: str


class HtmlRequest(BaseModel):
    html: str


class HtmlContentRequest(BaseModel):
    html_content: str
    url: str


class ReportRequest(BaseModel):
    evaluation: dict


app = FastAPI(
    title="FrontMind AI Agents API",
    description="API para la evaluación técnica automatizada de interfaces frontend bajo ISO/IEC 25010.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("captures").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)
Path("extracted_projects").mkdir(exist_ok=True)

app.mount("/captures", StaticFiles(directory="captures"), name="captures")


@app.get("/")
def home():
    return {
        "message": "FrontMind AI Agents API funcionando",
        "status": "ok",
        "version": "1.0.0",
    }


@app.post("/capture/url")
def capture_url(request: UrlRequest):
    agent = CaptureAgent()
    return agent.run(request.url)


@app.post("/replicate/html")
def replicate_html(request: UrlRequest):
    capture_agent = CaptureAgent()
    capture_result = capture_agent.run(request.url)

    html_agent = HtmlReplicationAgent()
    html_result = html_agent.run(
        html_content=capture_result.get("html_content", ""),
        url=capture_result.get("url", request.url),
    )

    return {
        "capture": capture_result,
        "html_replication": html_result,
    }


@app.post("/replicate/content")
def replicate_content(request: HtmlContentRequest):
    html_agent = HtmlReplicationAgent()

    html_result = html_agent.run(
        html_content=request.html_content,
        url=request.url,
    )

    return {
        "html_replication": html_result,
    }


@app.post("/evaluate/iso")
def evaluate_iso(request: HtmlRequest):
    agent = ISOEvaluationAgent()
    return agent.run(request.html)


@app.post("/report/generate")
def generate_report(request: ReportRequest):
    agent = ReportAgent()
    return agent.run({"evaluation": request.evaluation})


@app.post("/upload/zip")
async def upload_zip(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    zip_path = upload_dir / file.filename

    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_zip_project(str(zip_path))

    return {
        "source_type": "zip",
        "file_name": file.filename,
        "status": "processed",
        "extraction": result,
    }