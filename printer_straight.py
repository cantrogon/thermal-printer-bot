import win32ui
import win32gui
import win32con
from PIL import Image
import tempfile
import os

from printer_utils import open_image_from_url

def do_print_contents_straight(hdc, data):
    hdc.SetBkMode(win32con.TRANSPARENT)
    hdc.SetTextAlign(win32con.TA_LEFT | win32con.TA_TOP)
    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 32,
        "weight": win32con.FW_BOLD,
        "underline": False,
    })
    hdc.SelectObject(font)

    y_obj = [0]
    y_margin = 40

    for d in data:
        margin = d.get("margin") if d.get("margin") is not None else y_margin
        if d["type"] == "text":
            set_text(hdc, d["content"], y_obj, margin)
        elif d["type"] == "image_path":
            set_image(hdc, d["content"], y_obj, margin)
        elif d["type"] == "image_url":
            img = open_image_from_url(d["content"])
            set_image(hdc, img, y_obj, margin)

    set_text(hdc, ".", y_obj, y_margin)



def set_text(hdc, text, y_obj, y_margin):
    printable_width = hdc.GetDeviceCaps(win32con.HORZRES)
    
    rect = [0, y_obj[0], printable_width, 0]
    new_h = hdc.DrawText(text, rect, win32con.DT_CALCRECT | win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK)
    rect[3] = y_obj[0] + new_h
    hdc.DrawText(text, rect, win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK)

    y_obj[0] += new_h + y_margin


def set_image(hdc, image_path, y_obj, y_margin):
    # Load and convert the image to RGB
    image = Image.open(image_path).convert("RGB")

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


    printable_width = hdc.GetDeviceCaps(win32con.HORZRES)

    p = 0.6
    target_w = int(printable_width * p)
    target_h = int(target_w * image.size[1] / image.size[0])

    x_center = int((printable_width - target_w) / 2)

    # Draw the image at the specified coordinates
    win32gui.StretchBlt(
        hdc.GetSafeHdc(),  # Destination device context handle
        x_center, y_obj[0],  # Destination x, y coordinates
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

    y_obj[0] += target_h + y_margin



