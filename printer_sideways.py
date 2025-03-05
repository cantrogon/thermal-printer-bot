import win32ui
import win32gui
import win32con
from PIL import Image

from printer_utils import open_image_from_url, set_image, draw_filler_x

FONT_FAMILY = "Courier New"
FONT_WEIGHT = win32con.FW_BOLD

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
			"weight": FONT_WEIGHT
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
			"weight": FONT_WEIGHT
		})




def do_print_contents_sideways(hdc, data):
	set_sideways(hdc)

	hdc.SetBkMode(win32con.TRANSPARENT)
	hdc.SetTextAlign(win32con.TA_LEFT | win32con.TA_TOP)
	# font = win32ui.CreateFont({
	# 	"name": "Courier New",
	# 	"height": 300,
	# 	"weight": FONT_WEIGHT,
	# 	"underline": False,
	# })
	# hdc.SelectObject(font)

	horizontal_correction = 80 # corrects for printer offset

	wh_ratio = 63 / 88
	effective_height = hdc.GetDeviceCaps(win32con.HORZRES)
	effective_width = int(effective_height * wh_ratio)
	effective_width -= 20 # manual correction
	width_corrected = effective_width - horizontal_correction
	# print(effective_height)
	# print(effective_width)

	format_content(hdc, data, width_corrected, effective_height)
	draw_filler_x(hdc, effective_width)

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

