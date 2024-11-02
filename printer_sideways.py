import win32ui
import win32gui
import win32con
from PIL import Image
import tempfile
import os
import copy

from printer_utils import open_image_from_url

FONT_FAMILY = "Courier New"

def format_content(hdc, data, page_width, page_height):
	current_y = 0
	for d in data:

		height = int(d["height"] * page_height)
		padding_top = int(d.get("padding_top", 0) * height)
		padding_bottom = int(d.get("padding_bottom", 0) * height)

		if d["type"] == "text":
			rect = (0, current_y + padding_top, page_width, current_y + height - (padding_top + padding_bottom))
			draw_fitted_text(hdc, d["content"], rect)
		elif d["type"] == "image_path" or d["type"] == "image_url":
			img = d["content"] if d["type"] == "image_path" else open_image_from_url(d["content"])
			rect = (0, current_y + padding_top, page_width, height - (padding_top + padding_bottom))
			set_image(hdc, img, rect)

		current_y += height


def draw_fitted_text(hdc, text, rect):
	font = create_font_to_fit_text(hdc, text, rect)
	hdc.SelectObject(font)
	hdc.DrawText(text, rect, win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK)

def create_font_to_fit_text(hdc, text, rect):
	# Initialize font size range
	max_font_height = 600  # Starting from a large font size
	min_font_height = 10   # Minimum readable font size

	# Binary search to find the optimal font size
	best_font = None
	low = min_font_height
	high = max_font_height
	rect_height = rect[3] - rect[1]

	while low <= high:
		mid = (low + high) // 2
		font = win32ui.CreateFont({
			"name": FONT_FAMILY,
			"height": mid,
			"weight": win32con.FW_NORMAL
		})
		hdc.SelectObject(font)
		
		calc_rect = list(rect)
		flags = win32con.DT_CALCRECT | win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK
		text_height = hdc.DrawText(text, calc_rect, flags)
		
		if text_height < rect_height:
			best_font = font  # Text fits, try a larger font
			low = mid + 1
		else:
			high = mid - 1  # Text doesn't fit, try a smaller font

	if best_font:
		return best_font
	else:
		# Return the smallest font if none fit
		return win32ui.CreateFont({
			"name": FONT_FAMILY,
			"height": min_font_height,
			"weight": win32con.FW_NORMAL
		})




def do_print_contents_sideways(hdc, data):
	set_sideways(hdc)

	hdc.SetBkMode(win32con.TRANSPARENT)
	hdc.SetTextAlign(win32con.TA_LEFT | win32con.TA_TOP)
	font = win32ui.CreateFont({
		"name": "Courier New",
		"height": 300,
		"weight": win32con.FW_BOLD,
		"underline": False,
	})
	hdc.SelectObject(font)

	# Assuming print data is in the form:
	#  print_obj = [
	#     {"type": "text", "content": name},
	#     {"type": "image_url", "content": image_url},
	#     {"type": "text", "content": type_line},
	#     {"type": "text", "content": oracle_text},
	# ]
	# print_data = [
	# 	data[0]["content"], # title
	# 	open_image_from_url(data[1]["content"]), # image
	# 	data[2]["content"] + "\n\n" + data[3]["content"], # description
	# ]


	wh_ratio = 63 / 88
	effective_height = hdc.GetDeviceCaps(win32con.HORZRES)
	effective_width = int(effective_height * wh_ratio)

	format_content(hdc, data, effective_width, effective_height)

def set_sideways(hdc):
	page_width = hdc.GetDeviceCaps(win32con.HORZRES)
	hdc.SetGraphicsMode(win32con.GM_ADVANCED)
	xform = {
		"M11": 0,
		"M12": 1,
		"M21": -1,
		"M22": 0,
		"Dx": page_width,
		"Dy": 0,
	}
	win32gui.SetWorldTransform(hdc.GetHandleOutput(), xform)


def set_text(hdc, text, y_obj, y_margin):
	printable_width = hdc.GetDeviceCaps(win32con.HORZRES)
	
	rect = [0, y_obj[0], printable_width, 0]
	new_h = hdc.DrawText(text, rect, win32con.DT_CALCRECT | win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK)
	rect[3] = y_obj[0] + new_h
	hdc.DrawText(text, rect, win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK)

	y_obj[0] += new_h + y_margin


def set_image(hdc, image_path, rect):
	# Load and convert the image to RGB
	image = Image.open(image_path).convert("RGB")


	# Get image rect
	image_wh_ratio = image.size[0] / image.size[1]
	target_w = int(rect[3] * image_wh_ratio)
	target_h = rect[3]
	target_x = rect[0] + int((rect[2] - target_w) / 2) # center
	target_y = rect[1]


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



