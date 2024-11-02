import requests
import win32print
import win32ui
import win32gui
import win32con

from printer_sideways import do_print_contents_sideways
from printer_straight import do_print_contents_straight

def print_request(data, print_type="straight", printer_name=None):
    printer_name = printer_name if printer_name is not None else win32print.GetDefaultPrinter()

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc("Python Print Job")
    hdc.StartPage()

    if print_type == "straight":
        do_print_contents_straight(hdc, data)
    elif print_type == "sideways":
        do_print_contents_sideways(hdc, data)
    else:
        return None

    # End
    print("Sent to the printer.")
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()


