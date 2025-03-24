from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app instance

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Please refer swagger doc at /docs"}