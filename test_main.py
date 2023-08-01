from fastapi.testclient import TestClient
from main import app

# Sample test data
country_code = "US"
expected_common_name = "United States"

client = TestClient(app)

#   Test function for the health check endpoint.
#
#   Sends an HTTP GET request to the root endpoint ("/") of the FastAPI application.
#   Verifies that the response status code is 200 (OK).
#   Verifies that the response JSON data contains a "health_check" key with the value "Hello there!".
#
#   Example usage:
#   Run this test function using a testing framework such as pytest.
#
def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health_check": "Hello there!"}

#   Test function for the country details endpoint.
#
#   Sends an HTTP GET request to the "/countries/details/{country_code}" endpoint of the FastAPI application,
#   where {country_code} is set to the value of the "country_code" variable (e.g., "US" in this case).
#   Verifies that the response status code is 200 (OK).
#   Verifies that the response JSON data contains a "common_name" key with a value that matches the expected_common_name variable.
#
#   Example usage:
#   Run this test function using a testing framework such as pytest.
#
def test_country_details_endpoint():
    response = client.get(f"/countries/details/{country_code}")
    assert response.status_code == 200
    response_data = response.json()
    actual_common_name = response_data.get("common_name")
    assert actual_common_name == expected_common_name