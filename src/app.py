# Import necessary libraries
import serial  # For handling serial communication
import time  # For time-related functions
import pandas as pd  # For working with CSV files and data manipulation

# Custom modules for parsing weight data and handling OLED display
from parse import get_stable_weight, calculate_sku_quantity, oled_display

# Logging for error and event tracking
import logging
import sys
import os

# Paths for external resources
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# Waveshare OLED library and utilities for display management
from waveshare_OLED import OLED_2in42
from PIL import Image, ImageDraw, ImageFont

# Serial connection setup constants
PORT = '/dev/ttyUSB0'  # Define the serial port for the USB device
BAUDRATE = 1200  # Communication baud rate for the serial connection

# Weight deviation threshold and read duration for stable weight detection
WEIGHT_DEVIATION_THRESHOLD = 0.01  # Tolerance for weight fluctuation
READ_DURATION = 5  # Time duration to stabilize the weight reading

# Initialize the OLED display
try:
    disp = OLED_2in42.OLED_2in42(spi_freq=1000000)  # Set SPI frequency for display
    disp.Init()  # Initialize the display
    disp.clear()  # Clear the display for fresh use
except Exception as e:
    # Handle display initialization failure
    oled_display(disp, "Display initialization failed.", "")
    logging.error("Display initialization failed:", e)

# Load SKU weights from a CSV file
try:
    df = pd.read_csv('sku_weights.csv')  # Load SKU weights into a DataFrame
    oled_display(disp, "CSV Loaded.", "")
    print("SKU weights loaded successfully.")
except FileNotFoundError:
    # Handle missing CSV file error
    oled_display(disp, "CSV Not Found.", "")
    logging.error("Error: 'sku_weights.csv' file not found. Please ensure it is in the correct directory.")
    sys.exit("Missing CSV file: 'sku_weights.csv'")
except pd.errors.EmptyDataError:
    # Handle corrupted or empty CSV file
    oled_display(disp, "CSV Corrupted.", "")
    logging.error("Error: 'sku_weights.csv' is empty or corrupted.")
    sys.exit("Corrupted CSV file: 'sku_weights.csv'")
except Exception as e:
    # General error handling for CSV loading
    oled_display(disp, "CSV Read Error.", "")
    logging.error(f"Error loading 'sku_weights.csv': {e}")
    sys.exit("Unable to load CSV file.")

# Main program logic
if __name__ == "__main__":
    try:
        # Establish serial communication
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)  # Configure serial port
        print(f"Connected to {PORT} at {BAUDRATE} baud.")
        oled_display(disp, "Starting...", "")

        while True:
            # Display a message on the OLED prompting the user to scan a QR code
            print("\n\n\n")
            oled_display(disp, "Scan the QR Code", "")
            sku = input("Enter SKU...\n")  # Input SKU from the user
            oled_display(disp, "Counting...", "")
            print("Counting...")

            # Obtain stable weight from the scale
            weight = get_stable_weight(PORT, BAUDRATE, WEIGHT_DEVIATION_THRESHOLD, READ_DURATION)
            if weight:
                # Calculate quantity based on SKU and weight
                quantity = calculate_sku_quantity(sku, df, weight)
                if quantity:
                    # Display SKU and calculated quantity on the OLED
                    oled_display(disp, sku, f"QTY: {quantity}")
                else:
                    # Handle case where SKU is not found in the database
                    print("No SKU Found.")
                    oled_display(disp, "SKU not in database.", "")
                time.sleep(2)  # Adjust delay for user interaction as needed
    except serial.SerialException as e:
        # Handle errors related to serial port communication
        oled_display(disp, "Unable to connect to USB port.", "")
        logging.error(f"Error: Unable to connect to serial port {PORT}.")
        sys.exit(f"Serial connection error: {e}")
    except Exception as e:
        # Handle critical errors during serial communication initialization
        oled_display(disp, "Error initializing serial connection.", "")
        logging.error(f"Error initializing serial connection: {e}")
        sys.exit("Critical error: Serial connection failed.")
    except (KeyboardInterrupt, SystemExit):
        # Gracefully exit on user interruption
        print('Bye :)')
