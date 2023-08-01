import requests
import pytz
from PIL import Image
from io import BytesIO
from fastapi import FastAPI
import uvicorn


# Retrieves details of a country based on its country code using the restcountries.com API.
# Input: country_code (str) - The country code (e.g., "US", "IN", "FRA", "esp") in either lower or upper case.
# Output: Dictionary containing various country details.
#
#   The function sends an HTTP request to the API and retrieves data in JSON format.
#   It extracts relevant information, such as common name, official name, native name, local languages,
#   two-letter ISO code, and time zones associated with the country.
#
#   Raises an exception if the country is not found (HTTP status code is not 200).
#
#   Example usage:
#   >>> details = get_country_details("US")
#   >>> print(details["common_name"])  # Output: "United States"
#   >>> print(details["local_languages"])  # Output: {"eng": "English"}
#
#   Note: Some country codes might not exist in the API database, which could raise an exception.
#
def get_country_details(country_code):
    url = "https://restcountries.com/v3.1/alpha/"
    response = requests.get(url+country_code)
    if response.status_code != 200:
        raise Exception("Country not found")

    country_data = response.json()

    common_name = country_data[0]["name"]["common"]
    official_name = country_data[0]["name"]["official"]
    native_name = country_data[0]["name"]["nativeName"]
    local_languages = country_data[0]["languages"]
    two_letter_c_iso = country_data[0]["altSpellings"][0]
    country_tzs = pytz.country_timezones(two_letter_c_iso)

    return {
        "country_code": country_code.upper(),
        "iso_2_letter_code": two_letter_c_iso,
        "common_name": common_name,
        "official_name": official_name,
        "native_name(s)": native_name,
        "local_languages": local_languages,
        "time_zones": country_tzs
    }

# Retrieves the current date and time for a given time zone using the worldtimeapi.org API.
# Input: time_zone (str) - The time zone to fetch the current time for.
# the time zone data comes from the get_country_details and uses a second API to obtain the current time in the timezone
# Output: Dictionary containing the current date and time in ISO format.
#
#   The function sends an HTTP request to the API and retrieves data in JSON format.
#   It extracts the current date and time in ISO format for the specified time zone.
#
#   Example usage:
#   >>> current_time = get_current_time("America/New_York")
#   >>> print(current_time)  # Output: {"America/New_York": "2023-08-01T12:34:56.789Z"}
#
def get_current_time(time_zone):
    time_api_url = "https://worldtimeapi.org/api/timezone/"
    get_time_data = requests.get(time_api_url+time_zone).json()
    current_iso_date_time = get_time_data["datetime"]
    
    return {
        time_zone : current_iso_date_time
    }

# Retrieves the flag image of a country based on its country code using the restcountries.com API.
# Input: country_code (str) - The country code (e.g., "US", "IN", "FRA", "esp") in either lower or upper case.
# Output: Dictionary containing the output path where the flag image is saved and the image size.
#
#   The function sends an HTTP request to the API and retrieves the flag image URL in PNG format.
#   It then downloads the image, resizes it to a maximum width of 250 pixels while preserving the aspect ratio,
#   and saves it to a local directory (public/).
#
#   Returns the path where the resized flag image is saved and its size.
#
#   Example usage:
#   >>> flag_data = get_country_flag("US")
#   >>> print(flag_data["output_path"])  # Output: "public/US_flag_250.png"
#   >>> print(flag_data["image_size"])  # Output: (250, 160)
#
def get_country_flag(country_code):
    url = "https://restcountries.com/v3.1/alpha/"
    response = requests.get(url + country_code).json()

    flag_meta = response[0]["flags"]["png"]
    response_img = requests.get(flag_meta)
    response_img.raise_for_status()  # Raise an exception for HTTP errors

    img = Image.open(BytesIO(response_img.content))
    max_width = 250
    width_percent = (max_width / float(img.size[0]))
    new_height = int((float(img.size[1]) * float(width_percent)))
    resized_img = img.resize((max_width, new_height), Image.LANCZOS)

    output_path = f"public/{country_code}_flag_250.png"
    resized_img.save(output_path)

    return {
        "output_path": output_path,
        "image_size": resized_img.size
    }

# Create a FastAPI instance.
app = FastAPI()

# API endpoint to perform a health check.
#
#   Returns a simple JSON response indicating the service is healthy.
#
#   Example usage:
#   Visit http://localhost:8000/ in your web browser or send an HTTP GET request to the endpoint.
#   Response: {"health_check": "Hello there!"}
#
@app.get("/")
def read_root():
    return {
        "health_check": "Hello there!"
    }

# API endpoint to get details of a country by country code.
#
#   It internally calls the get_country_details function to fetch country details.
#   It also retrieves the current time for each time zone associated with the country.
#
#   Returns a JSON response containing common name, official name, native name, local languages,
#   and a list of current date and time in ISO format for each time zone.
#
#   Example usage:
#   Visit http://localhost:8000/countries/details/US in your web browser or send an HTTP GET request to the endpoint.
#   Response: {"common_name": "United States", "official_name": "United States of America",
#              "native_name": {"eng": "United States"}, "local_languages": {"eng": "English"},
#              "current_times": [{"America/New_York": "2023-08-01T12:34:56.789Z"},
#                                {"America/Chicago": "2023-08-01T09:34:56.789Z"},
#                                {"America/Denver": "2023-08-01T07:34:56.789Z"},
#                                {"America/Los_Angeles": "2023-08-01T06:34:56.789Z"}]}
#
@app.get("/countries/details/{country_code}")
async def country_details(country_code: str):
    country_data = get_country_details(country_code)
    country_local_times = get_country_details(country_code)["time_zones"]
    current_times = [get_current_time(timezone) for timezone in country_local_times]

    return {
        "common_name": country_data["common_name"],
        "official_name": country_data["official_name"],
        "native_name": country_data["native_name(s)"],
        "local_languagues": country_data["local_languages"],
        "current_time(s)": current_times
    }

# API endpoint to get the flag of a country by country code.
#
#   It internally calls the get_country_flag function to fetch the country's flag image.
#   The resized flag image is then served as a response.
#
#   Example usage:
#   Visit http://localhost:8000/countries/flags/US in your web browser or send an HTTP GET request to the endpoint.
#   The flag image will be displayed in your browser, and the file will be saved in the "public/" directory.
#
@app.get("/countries/flags/{country_code}")
async def get_flag(country_code: str):
    country_flag_data = get_country_flag(country_code)
    return country_flag_data

# If the script is run as the main module, start the FastAPI server.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)