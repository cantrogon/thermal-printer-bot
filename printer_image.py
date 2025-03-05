from printer_utils import set_image, set_image_from_image, draw_filler_y
import win32con

def do_print_image(hdc, image):
	page_width = hdc.GetDeviceCaps(win32con.HORZRES)
	rect = (0, 0, page_width, 0)
	img_rect = set_image_from_image(hdc, image, rect, image_fit="overflow_y")
	draw_filler_y(hdc, img_rect[3] + 100) # vertical printer correction
