import os
from math import ceil
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from jinja2 import Environment, FileSystemLoader
from starlette.responses import HTMLResponse

from utils.image_utils import create_thumbnail
from utils.json_utils import read_json_file

app = FastAPI()

# Folder containing the JSON files
data_folder = "listing"


def sort_by_list() -> list:
    return [
        'rent', 'bedrooms', 'bathrooms', 'area', 'price_per_sqm',
    ]


@app.get("/", response_class=HTMLResponse)
def get_countries(request: Request):
    countries = [country_name for country_name in os.listdir(data_folder) if
                 os.path.isdir(os.path.join(data_folder, country_name))]
    template = "countries.html"
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template)
    context = {"request": request, "countries": countries}
    return template.render(context)


@app.get("/{country_name}/", response_class=HTMLResponse)
def get_country_listing(
        country_name: str,
        sort_key: str = 'rent',
        order: Optional[str] = "asc",
        page: int = 1,
):
    country_folder_path = os.path.join(data_folder, country_name)
    if os.path.exists(country_folder_path) and os.path.isdir(country_folder_path):
        json_objects = []
        for file_name in os.listdir(country_folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(country_folder_path, file_name)
                file_data = read_json_file(file_path)
                if file_data:
                    for item in file_data:
                        json_objects.append(item)

        if json_objects:
            sorted_json_objects = sorted(json_objects, key=lambda x: x.get(sort_key, 0))

            items_per_page = 12
            total_items = len(sorted_json_objects)
            total_pages = ceil(total_items / items_per_page)

            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            items_for_page = sorted_json_objects[start_idx:end_idx]

            if order == "desc":
                items_for_page = sorted(items_for_page, key=lambda x: x.get(sort_key, 0), reverse=True)
            else:
                items_for_page = sorted(items_for_page, key=lambda x: x.get(sort_key, 0))

            template = "sorted_data.html"
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template(template)
            context = {
                "country_name": country_name,
                "sorted_json_objects": items_for_page,
                "current_page": page,
                "total_pages": total_pages,
                "create_thumbnail": create_thumbnail,
                "sort_key": sort_key,
                "order": order,
                "sort_by_list": sort_by_list(),
            }
            return template.render(context)

        else:
            raise HTTPException(status_code=404, detail="No JSON files found in the country folder")
    else:
        raise HTTPException(status_code=404, detail="Country folder not found")
