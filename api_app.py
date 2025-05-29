from __future__ import annotations
import os
import tempfile
import json
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from parser import parse
from rag import sim_search, determine_pyobj, retrieve_data_from_llm
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from dotenv import load_dotenv

load_dotenv()


def process_grant(files: list[str], k: int = 4, model: str | None = None) -> dict:
    """Process one or more PDF files and return grant info as a dict."""
    if model:
        os.environ["MODEL"] = model

    print("parsing files")
    pages = parse(files)
    print("making embeddings")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = InMemoryVectorStore.from_documents(pages, embeddings)

    llm_queries = {
        "general": (
            "What is the full name of the grant? List all projects or programs stated, including each project's name, start date, and end date."
        ),
        "spending": (
            "What is the total grant amount? Break down the spending into: salary, fringe/payroll benefits, indirect costs, travel, equipment, and other. For \u201cother,\u201d provide a list of items with their names and cost. Return only valid JSON."
        ),
    }
    vec_queries = {
        "general": (
            "Information about the grant's official name, and the names, start and end dates of any funded projects or programs."
        ),
        "spending": (
            "Details about total funding, and how the grant money is allocated \u2014 including salary, fringe/payroll benefits, indirect costs, travel, equipment, and other types of spending."
        ),
    }

    print("running LLM queries")
    grant_json: dict[str, object] = {}
    for key in llm_queries:
        context = sim_search(vec_queries[key], k, vector_store)
        py_obj = determine_pyobj(key)
        response = retrieve_data_from_llm(llm_queries[key], context, py_obj)
        grant_json.update(response)
    print("returning json")
    print(grant_json)

    return grant_json


bearer = HTTPBearer()
basic = HTTPBasic()
app = FastAPI()

TOKEN = os.getenv("API_TOKEN")
WEB_USER = os.getenv("WEB_USER")
WEB_PASS = os.getenv("WEB_PASS")
DEFAULT_MODEL = os.getenv("MODEL")


@app.post("/api/grant")
async def post_grant(
    files: list[UploadFile] = File(...),
    k: int = 5,
    model: str | None = None,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    if not TOKEN or creds.credentials != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    paths: list[str] = []
    try:
        for f in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(await f.read())
                paths.append(tmp.name)
        result = process_grant(paths, k=k, model=model)
    finally:
        for p in paths:
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
    return result

_FORM = "<form method='post' enctype='multipart/form-data'>"
_FORM += "<input type='file' name='files' multiple><br>"
_FORM += "k: <input type='number' name='k' value='5'> (default 5)<br>"
_FORM += "model: <input type='text' name='model' value='"+DEFAULT_MODEL+"'> (default "+DEFAULT_MODEL+")<br>"
_FORM += "<button type='submit'>Submit</button>"
_FORM += "</form>"


def _check_basic(creds: HTTPBasicCredentials) -> None:
    correct = bool(WEB_USER and WEB_PASS and creds.username == WEB_USER and creds.password == WEB_PASS)
    if not correct:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})


@app.get("/web", response_class=HTMLResponse)
async def get_web(creds: HTTPBasicCredentials = Depends(basic)):
    _check_basic(creds)
    return HTMLResponse(_FORM)


@app.post("/web", response_class=HTMLResponse)
async def post_web(
    creds: HTTPBasicCredentials = Depends(basic),
    files: list[UploadFile] = File(...),
    k: int = 4,
    model: str | None = None,
):
    _check_basic(creds)
    paths: list[str] = []
    try:
        for f in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(await f.read())
                paths.append(tmp.name)
        result = process_grant(paths, k=k, model=model)
        data = json.dumps(result, indent=2)
    finally:
        for p in paths:
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
    return HTMLResponse(_FORM + f"<pre>{data}</pre>")
