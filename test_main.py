from fastapi.testclient import TestClient
from main import app

# Sample test data
country_code = "US"
expected_common_name = "United States"

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health_check": "Hello there!"}

def test_country_details_endpoint():
    response = client.get(f"/countries/details/{country_code}")
    assert response.status_code == 200
    response_data = response.json()
    actual_common_name = response_data.get("common_name")
    assert actual_common_name == expected_common_name