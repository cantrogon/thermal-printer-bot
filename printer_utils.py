from io import BytesIO
from PIL import Image
import requests
import tempfile
import os
import win32gui
import win32ui
import win32con

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


def set_image_from_image(hdc, image_data, rect, image_fit="contain"):
	image_file = BytesIO(image_data)
	return set_image(hdc, image_file, rect, image_fit)

def set_image(hdc, image_path, rect, image_fit="contain"):
	# Load and convert the image to RGB
	image = Image.open(image_path).convert("RGB")

	# Get image rect
	target_x, target_y, target_w, target_h = get_image_rect(image, rect, image_fit)

	# Create a temporary file to hold the BMP image
	with tempfile.NamedTemporaryFile(delete=False, suffix='.bmp') as temp_file:
		bmp_file_path = temp_file.name
		image.save(bmp_file_path, format='BMP')

	hdc_bitmap = win32gui.LoadImage(
		0,  # hInstance, 0 for loading from file
		bmp_file_path,  # File path to the BMP file
		win32gui.IMAGE_BITMAP,  # Image type
		0, 0,  # Desired width and height (0 to use the actual size)
		win32gui.LR_LOADFROMFILE | win32gui.LR_CREATEDIBSECTION  # Load from file and create a DIB section
	)


	# Create a compatible device context and select the bitmap into it
	mem_dc = hdc.CreateCompatibleDC()
	mem_dc.SelectObject(win32ui.CreateBitmapFromHandle(hdc_bitmap))

	# Draw the image at the specified coordinates
	win32gui.StretchBlt(
		hdc.GetSafeHdc(),  # Destination device context handle
		target_x, target_y,  # Destination x, y coordinates
		target_w, target_h,  # Destination width and height
		mem_dc.GetSafeHdc(),  # Source device context handle
		0, 0,  # Source x, y coordinates
		image.size[0], image.size[1],  # Source width and height
		win32con.SRCCOPY  # Raster operation code
	)

	# Clean up
	mem_dc.DeleteDC()
	
	# Remove the temporary BMP file
	os.remove(bmp_file_path)

	return target_x, target_y, target_w, target_h


def get_image_rect(image, rect, image_fit=None):
	image_w, image_h = image.size
	image_wh_ratio = image_w / image_h
	
	if image_fit == 'overflow_y':
		rect = list(rect)
		target_w = rect[2]
		target_h = int(image_h * rect[2] / image_w)
		rect[3] = target_h
	else: # 'contain' default
		rect_wh_ratio = rect[2] / rect[3]
		if image_wh_ratio > rect_wh_ratio: # image is proportionally wider than rect
			target_w = rect[2]
			target_h = int(rect[2] / image_wh_ratio)
		else:
			target_w = int(rect[3] * image_wh_ratio)
			target_h = rect[3]
	
	# centers image
	target_x = rect[0] + int((rect[2] - target_w) / 2)
	target_y = rect[1] + int((rect[3] - target_h) / 2)

	return target_x, target_y, target_w, target_h

def draw_filler(hdc, rect):
	font = win32ui.CreateFont({
		"name": "Arial",
		"height": 10,
		"weight": win32con.FW_NORMAL,
	})
	hdc.SelectObject(font)
	hdc.DrawText("T", rect, win32con.DT_LEFT | win32con.DT_TOP)

def draw_filler_x(hdc, w):
	rect = (w - 1, 0, w, 10)
	draw_filler(hdc, rect)

def draw_filler_y(hdc, h):
	rect = (0, h - 10, 10, h)
	draw_filler(hdc, rect)

