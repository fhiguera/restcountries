import requests
import pytz
from PIL import Image
from io import BytesIO
from fastapi import FastAPI
import uvicorn

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

def get_current_time(time_zone):
    time_api_url = "https://worldtimeapi.org/api/timezone/"
    get_time_data = requests.get(time_api_url+time_zone).json()
    current_iso_date_time = get_time_data["datetime"]
    
    return {
        time_zone : current_iso_date_time
    }

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

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "health_check": "Hello there!"
    }

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

@app.get("/countries/flags/{country_code}")
async def get_flag(country_code: str):
    country_flag_data = get_country_flag(country_code)
    return country_flag_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)