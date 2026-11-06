import asyncio
import base64
import tempfile
import zipfile
from pathlib import Path

import pytest
import pandas as pd
from fastapi.testclient import TestClient

import app as app_module
from app import DataAnalyst, app, get_llm_model, parse_json_response

client = TestClient(app)

def test_root_and_health_endpoints():
    home = client.get("/")
    assert home.status_code == 200
    assert home.headers["content-type"].startswith("text/html")
    head = client.head("/")
    assert head.status_code == 200
    assert head.content == b""
    assert "Make your data" in home.text
    assert client.get("/static/app.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

def test_default_model_is_gemma_4(monkeypatch):
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    assert get_llm_model() == "google/gemma-4-26b-a4b-it"

def test_missing_questions_file_is_bad_request():
    response = client.post("/api/", files={"data.csv": ("data.csv", b"value\n1\n", "text/csv")})
    assert response.status_code == 400

def test_csv_upload_works_without_an_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it")
    files = {
        "questions.txt": ("questions.txt", b"How many rows are in the dataset?", "text/plain"),
        "data.csv": ("../safe-name.csv", b"value\n10\n20\n30\n", "text/csv"),
    }
    response = client.post("/api/", files=files)
    assert response.status_code == 200
    assert response.json() == [3]

def test_oversized_file_respects_configured_limit(monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "4")
    monkeypatch.setenv("MAX_TOTAL_UPLOAD_BYTES", "1024")
    files = {
        "questions.txt": ("questions.txt", b"count rows", "text/plain"),
        "data.csv": ("data.csv", b"value\\n123\\n", "text/csv"),
    }
    response = client.post("/api/", files=files)
    assert response.status_code == 413



def test_memory_guard_rejects_dataset_before_pandas_load(monkeypatch, tmp_path):
    dataset = tmp_path / "large.csv"
    dataset.write_bytes(b"value\n" + (b"1\n" * (2 * 1024 * 1024)))
    monkeypatch.setattr(app_module, "get_available_memory_bytes", lambda: 100 * 1024 * 1024)
    monkeypatch.setenv("DATA_MEMORY_MULTIPLIER", "3")
    monkeypatch.setenv("MIN_MEMORY_RESERVE_BYTES", str(96 * 1024 * 1024))
    with pytest.raises(app_module.HTTPException) as exc:
        app_module.guard_dataset_memory([str(dataset)])
    assert exc.value.status_code == 413
    assert "higher-memory instance" in exc.value.detail


def test_memory_guard_allows_small_dataset_when_memory_is_available(monkeypatch, tmp_path):
    dataset = tmp_path / "small.csv"
    dataset.write_bytes(b"value\n1\n")
    monkeypatch.setattr(app_module, "get_available_memory_bytes", lambda: 256 * 1024 * 1024)
    app_module.guard_dataset_memory([str(dataset)])

def test_zip_path_traversal_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive_path = root / "malicious.zip"
        extraction_path = root / "extracted"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("../outside.txt", "should not be written")
        analyst = DataAnalyst()
        with pytest.raises(ValueError):
            asyncio.run(analyst.extract_archive(str(archive_path), str(extraction_path)))
        assert not (root / "outside.txt").exists()

def test_safe_zip_extracts_supported_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive_path = root / "valid.zip"
        extraction_path = root / "extracted"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("dataset.csv", "value\n1\n2\n")
        analyst = DataAnalyst()
        extracted = asyncio.run(analyst.extract_archive(str(archive_path), str(extraction_path)))
        assert len(extracted) == 1
        assert Path(extracted[0]).name == "dataset.csv"

def test_json_parser_handles_markdown_fences():
    raw = "```json" + chr(10) + '[1, "ok"]' + chr(10) + "```"
    assert parse_json_response(raw) == [1, "ok"]

def test_openrouter_client_uses_openrouter_base_url(monkeypatch):
    captured = {}
    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)
    monkeypatch.setattr(app_module, "OpenAI", FakeClient)
    monkeypatch.setattr(app_module, "client", None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    assert app_module.get_openai_client() is not None
    assert captured["api_key"] == "test-key"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["default_headers"]["X-Title"] == "TDS Data Analyst Agent"

def test_visualization_payload_is_bounded():
    data = pd.DataFrame({"x": list(range(100)), "y": [value ** 2 for value in range(100)]})
    uri = DataAnalyst().create_visualization(data)
    header, encoded = uri.split(",", 1)
    assert header in {"data:image/png;base64", "data:image/webp;base64"}
    assert len(base64.b64decode(encoded)) <= 100_000
