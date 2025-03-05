import requests
import win32print
import win32ui
import win32gui
import win32con

from printer_sideways import do_print_contents_sideways
from printer_straight import do_print_contents_straight
from printer_image import do_print_image

def print_request(data, print_type="straight", printer_name=None):
    result = None

    # printer_name = printer_name if printer_name is not None else win32print.GetDefaultPrinter()
    printer_name = "SAM4S ELLIX30"
    # printer_name = "Microsoft Print to PDF"

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("Python Print Job")
    hdc.StartPage()


    if print_type == "straight":
        result = do_print_contents_straight(hdc, data)
    elif print_type == "sideways":
        result = do_print_contents_sideways(hdc, data)
    elif print_type == "image":
        result = do_print_image(hdc, data)

    # End
    print("Sent to the printer.")
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

    return result

