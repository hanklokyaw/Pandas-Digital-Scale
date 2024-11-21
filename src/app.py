import serial
import time
import pandas as pd

from parse import get_stable_weight, calculate_sku_quantity, oled_display

import logging
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_OLED import OLED_2in42
from PIL import Image, ImageDraw, ImageFont

# Read the CSV file into a DataFrame
df = pd.read_csv('sku_weights.csv')

# Serial connection setup
PORT = '/dev/ttyUSB0'
BAUDRATE = 1200

# Global variable for weight deviation threshold
WEIGHT_DEVIATION_THRESHOLD = 0.01
READ_DURATION = 5

# Initialize the display
try:
    disp = OLED_2in42.OLED_2in42(spi_freq=1000000)
    disp.Init()
    disp.clear()

except Exception as e:
    logging.error("Display initialization failed:", e)

if __name__ == "__main__":

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {PORT} at {BAUDRATE} baud.")
        oled_display(disp, "Starting...", "")

        while True:
            print("\n\n\n")
            oled_display(disp, "Scan the QR Code", "")
            sku = input("Enter SKU...\n")
            oled_display(disp, "Counting...", "")
            print("Counting...")
            weight = get_stable_weight(PORT, BAUDRATE, WEIGHT_DEVIATION_THRESHOLD, READ_DURATION)
            if weight:
                quantity = calculate_sku_quantity(sku, df, weight)
                if quantity:
                    oled_display(disp, sku, f"QTY: {quantity}")
                else:
                    print("No SKU Found.")
                    oled_display(disp, "SKU not in database.", "")
                time.sleep(2)  # Adjust the delay as necessary for your use case

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')
