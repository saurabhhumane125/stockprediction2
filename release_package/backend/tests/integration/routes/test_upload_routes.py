import pytest
from fastapi import status
from pathlib import Path

from app.services.upload_service import upload_service

@pytest.fixture
def clean_uploads():
    """Fixture to clean up uploads directory before and after tests."""
    upload_dir = upload_service.upload_dir
    
    def cleanup():
        if upload_dir.exists():
            for f in upload_dir.iterdir():
                if f.is_file():
                    f.unlink()
                    
    cleanup()
    yield
    cleanup()

def test_valid_image_upload(client, clean_uploads):
    file_content = b"fake_image_content"
    files = {"file": ("test.png", file_content, "image/png")}
    
    response = client.post("/api/v1/vision/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == f"{data['hash']}.png"
    assert data["mime_type"] == "image/png"
    assert data["size_bytes"] == len(file_content)
    assert data["status"] == "success"

def test_invalid_mime_type(client, clean_uploads):
    file_content = b"fake_pdf_content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    
    response = client.post("/api/v1/vision/upload", files=files)
    
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "Unsupported file type" in response.json()["detail"]

def test_oversized_upload(client, clean_uploads, monkeypatch):
    monkeypatch.setattr(upload_service, "MAX_FILE_SIZE", 10)
    
    file_content = b"this_is_larger_than_10_bytes"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    response = client.post("/api/v1/vision/upload", files=files)
    
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    assert "File too large" in response.json()["detail"]

def test_duplicate_upload(client, clean_uploads):
    file_content = b"duplicate_test_content"
    files1 = {"file": ("test1.png", file_content, "image/png")}
    
    # Needs to be recreated because TestClient consumes the file-like object or bytes tuple correctly
    res1 = client.post("/api/v1/vision/upload", files=files1)
    assert res1.status_code == status.HTTP_200_OK
    hash1 = res1.json()["hash"]
    
    files2 = {"file": ("test2.png", file_content, "image/png")}
    res2 = client.post("/api/v1/vision/upload", files=files2)
    assert res2.status_code == status.HTTP_200_OK
    hash2 = res2.json()["hash"]
    
    assert hash1 == hash2
    
    upload_dir = upload_service.upload_dir
    matching_files = list(upload_dir.glob(f"{hash1}.*"))
    assert len(matching_files) == 1

def test_malware_rejection(client, clean_uploads, monkeypatch):
    from app.services.malware_scanner import malware_scanner
    
    monkeypatch.setattr(malware_scanner, "scan", lambda file_path: False)
    
    file_content = b"malicious_payload"
    files = {"file": ("virus.png", file_content, "image/png")}
    
    response = client.post("/api/v1/vision/upload", files=files)
    
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert "File rejected by malware scanner" in response.json()["detail"]
    
    upload_dir = upload_service.upload_dir
    files_on_disk = list(upload_dir.iterdir())
    assert len(files_on_disk) == 0
