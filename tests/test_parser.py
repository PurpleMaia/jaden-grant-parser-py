import json
import os
import importlib.util
import sys
from pathlib import Path
from langchain_core.documents import Document
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "parser", ROOT / "parser.py"
)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
sys.modules['parser'] = parser

class FakeLoader:
    def __init__(self, *args, **kwargs):
        pass
    def lazy_load(self):
        return [Document(page_content="content", metadata={"page":1}), Document(page_content="content2", metadata={"page":2})]

def test_parse_returns_pages(monkeypatch):
    """parse() should return all pages from multiple PDFs."""
    # Patch PyPDFLoader in parser module so each PDF yields two pages
    monkeypatch.setattr(parser, 'PyPDFLoader', lambda *a, **k: FakeLoader())
    pages = parser.parse(["dummy1.pdf", "dummy2.pdf"])
    assert isinstance(pages, list)
    assert len(pages) == 4
    assert all(isinstance(p, Document) for p in pages)

class FakeLLM:
    def __init__(self, *args, **kwargs):
        pass
    def invoke(self, prompt: str):
        return '{"foo": "bar"}'
    __call__ = invoke

class ExampleModel(BaseModel):
    foo: str

def test_retrieve_data_from_llm(monkeypatch):
    import rag
    monkeypatch.setattr(rag, 'ChatOpenAI', lambda *a, **k: FakeLLM())
    result = rag.retrieve_data_from_llm('question', 'context', ExampleModel)
    assert isinstance(result, dict)
    json.loads(json.dumps(result))
    assert result == {"foo": "bar"}
