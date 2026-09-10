import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job():
    response = client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description_raw": "Looking for a Python developer."},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Job"
    assert data["weight_semantic"] == 0.5


def test_get_job_not_found():
    response = client.get("/api/v1/jobs/999999")
    assert response.status_code == 404


def test_get_job_after_create():
    create_response = client.post(
        "/api/v1/jobs/",
        json={"title": "Fetch Test Job", "description_raw": "Test description."},
    )
    job_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Fetch Test Job"


def test_list_jobs_returns_list():
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_job_weights():
    create_response = client.post(
        "/api/v1/jobs/",
        json={"title": "Weights Test Job", "description_raw": "Test."},
    )
    job_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/jobs/{job_id}/weights",
        json={"weight_semantic": 0.7, "weight_skills": 0.3},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["weight_semantic"] == 0.7
    assert data["weight_skills"] == 0.3
    assert data["weight_experience"] == 0.15


def test_update_job_weights_not_found():
    response = client.put(
        "/api/v1/jobs/999999/weights",
        json={"weight_semantic": 0.9},
    )
    assert response.status_code == 404


def test_upload_candidate_rejects_unsupported_file_type():
    create_response = client.post(
        "/api/v1/jobs/",
        json={"title": "Upload Test Job", "description_raw": "Test."},
    )
    job_id = create_response.json()["id"]

    files = {"files": ("resume.txt", io.BytesIO(b"plain text content"), "text/plain")}
    response = client.post(f"/api/v1/jobs/{job_id}/candidates", files=files)

    assert response.status_code == 200
    data = response.json()
    assert len(data["failed"]) == 1
    assert data["failed"][0]["reason"] == "Unsupported file type"


def test_upload_candidate_job_not_found():
    files = {"files": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    response = client.post("/api/v1/jobs/999999/candidates", files=files)
    assert response.status_code == 404


def test_list_candidates_for_job():
    create_response = client.post(
        "/api/v1/jobs/",
        json={"title": "Candidates List Test Job", "description_raw": "Test."},
    )
    job_id = create_response.json()["id"]

    response = client.get(f"/api/v1/jobs/{job_id}/candidates")
    assert response.status_code == 200
    assert response.json() == []


def test_search_with_no_candidates_returns_400():
    create_response = client.post(
        "/api/v1/jobs/",
        json={"title": "Empty Search Test Job", "description_raw": "Test."},
    )
    job_id = create_response.json()["id"]

    response = client.post(f"/api/v1/jobs/{job_id}/search")
    assert response.status_code == 400
