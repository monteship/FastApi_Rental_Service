import io

import requests
from PIL import Image


def create_thumbnail(image_url, size=(400, 400)):
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))
    img.thumbnail(size)
    return img
