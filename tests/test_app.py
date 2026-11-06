import asyncio
import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import DataAnalyst, app, get_llm_model

client = TestClient(app)

def test_root_and_health_endpoints():
    assert client.get("/").status_code == 200
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

def test_default_model_is_gemma_4(monkeypatch):
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    assert get_llm_model() == "google/gemma-4-26b-a4b-it"

def test_missing_questions_file_is_bad_request():
    response = client.post("/api/", files={"data.csv": ("data.csv", b"value\\n1\\n", "text/csv")})
    assert response.status_code == 400

def test_csv_upload_works_without_an_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it")
    files = {
        "questions.txt": ("questions.txt", b"How many rows are in the dataset?", "text/plain"),
        "data.csv": ("../safe-name.csv", b"value\\n10\\n20\\n30\\n", "text/csv"),
    }
    response = client.post("/api/", files=files)
    assert response.status_code == 200
    assert response.json() == [3]

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
            archive.writestr("dataset.csv", "value\\n1\\n2\\n")
        analyst = DataAnalyst()
        extracted = asyncio.run(analyst.extract_archive(str(archive_path), str(extraction_path)))
        assert len(extracted) == 1
        assert Path(extracted[0]).name == "dataset.csv"
