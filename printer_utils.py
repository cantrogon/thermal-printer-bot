from io import BytesIO
from PIL import Image
import requests

def open_image_from_url(url):
    try:
        # Fetch the image data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Open the image using Pillow
        return BytesIO(response.content)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the image: {e}")
        return None
    except IOError as e:
        print(f"An error occurred while opening the image: {e}")
        return None
