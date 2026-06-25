import json
import os
import sys
from datetime import datetime
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
from services.screenshot_service import take_screenshots, take_screenshots_from_html, take_screenshots_for_multiple_htmls
from services.zip_service import extract_zip_project
from services.history_service import add_entry, load_history


class CredentialsModel(BaseModel):
    login_url: str | None = None
    username_selector: str | None = None
    username_value: str | None = None
    password_selector: str | None = None
    password_value: str | None = None
    submit_selector: str | None = None

class UrlRequest(BaseModel):
    url: str
    credentials: CredentialsModel | None = None

class HtmlRequest(BaseModel):
    html: str


class IsoRequest(BaseModel):
    html: str
    user_id: str | None = None



class ReportRequest(BaseModel):
    evaluation: dict
    user_id: str | None = None

class HtmlContentRequest(BaseModel):
    html_content: str
    url: str
    css_cache: dict | None = None
    cssom_styles: list | None = None


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
Path("../extracted_projects_temp").resolve().mkdir(exist_ok=True)

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
    return agent.run(request.url, request.credentials)


@app.post("/replicate/html")
def replicate_html(request: UrlRequest):
    capture_agent = CaptureAgent()
    capture_result = capture_agent.run(request.url, request.credentials)

    html_agent = HtmlReplicationAgent()
    html_result = html_agent.run(
        html_content=capture_result.get("html_content", ""),
        url=capture_result.get("url", request.url),
        css_cache=capture_result.get("css_cache", {}),
        cssom_styles=capture_result.get("cssom_styles", []),
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
        css_cache=request.css_cache,
        cssom_styles=request.cssom_styles,
    )

    return {
        "html_replication": html_result,
    }


@app.post("/evaluate/iso")
def evaluate_iso(request: IsoRequest):
    agent = ISOEvaluationAgent()
    return agent.run(request.html)

@app.get("/history")
def get_history(user_id: str | None = None):
    history = load_history()
    if user_id:
        history = [h for h in history if h.get("user_id") == user_id]
    return history


@app.post("/report/generate")
def generate_report(request: ReportRequest):
    agent = ReportAgent()
    result = agent.run({"evaluation": request.evaluation})
    # Record the evaluation in history at the moment of generating the report
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": request.user_id,
        "evaluation": request.evaluation,
        "report": result,
    }
    add_entry(entry)
    return result


@app.post("/upload/zip")
def upload_zip(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    zip_path = upload_dir / file.filename

    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_zip_project(str(zip_path))

    # Build dict of HTML contents to capture screenshots for
    htmls_to_capture = {}
    combined_html = result.get("combined_html", "")
    if combined_html and result.get("status") != "error":
        htmls_to_capture["combined"] = combined_html

    interfaces = result.get("interfaces", [])
    for iface in interfaces:
        fname = iface.get("file_name", "")
        hcontent = iface.get("html_content", "")
        if fname and hcontent:
            htmls_to_capture[fname] = hcontent

    captures = []
    if htmls_to_capture:
        try:
            label_prefix = file.filename.replace(".zip", "").replace(" ", "_")[:20]
            screenshot_results = take_screenshots_for_multiple_htmls(
                htmls_to_capture,
                label_prefix=label_prefix
            )
            # 1. Assign combined captures
            captures = screenshot_results.get("combined", [])
            # 2. Assign captures to each interface
            for iface in interfaces:
                fname = iface.get("file_name", "")
                iface["captures"] = screenshot_results.get(fname, [])
        except Exception as e:
            # Screenshots are best-effort — don't fail the whole request
            import traceback
            tb_str = traceback.format_exc()
            captures = [{"error": f"Exception in main.py:\n{tb_str}", "device": "all"}]

    return {
        "source_type": "zip",
        "file_name": file.filename,
        "status": "processed",
        "extraction": result,
        "captures": captures,
        "html_content": combined_html,
    }