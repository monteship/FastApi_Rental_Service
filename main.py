import json
import os
from urllib import request

from fastapi import FastAPI, HTTPException
from jinja2 import Environment, FileSystemLoader
from starlette.responses import HTMLResponse

app = FastAPI()

# Folder containing the JSON files
data_folder = "listing"


def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        # Handle empty or invalid JSON files here
        return None


@app.get("/", response_class=HTMLResponse)
def get_countries():
    countries = [country_name for country_name in os.listdir(data_folder) if
                 os.path.isdir(os.path.join(data_folder, country_name))]
    template = "templates/countries.html"
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template)
    context = {"request": request, "countries": countries}
    return template.render(context)


@app.get("/{country_name}/{sort_key}", response_class=HTMLResponse)
def get_country_listing(country_name: str, sort_key: str):
    country_folder_path = os.path.join(data_folder, country_name)
    if os.path.exists(country_folder_path) and os.path.isdir(country_folder_path):
        json_data = {}
        for file_name in os.listdir(country_folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(country_folder_path, file_name)
                file_data = read_json_file(file_path)
                if file_data:
                    json_data.update(file_data)

        if json_data:
            sorted_json_objects = sorted(json_data.values(), key=lambda x: x.get(sort_key, 0))
            return sorted_json_objects
        else:
            raise HTTPException(status_code=404, detail="No JSON files found in the country folder")
    else:
        raise HTTPException(status_code=404, detail="Country folder not found")
