import serial
import time
import pandas as pd
from parse import reset_timer_if_exceeded, parse_weight, calculate_deviation, calculate_bags, offset_light_weight_sku, get_weight_by_sku, calculate_sku_quantity, get_stable_weight
import os

# Read the CSV file into a DataFrame
df = pd.read_csv('sku_weights.csv')

# Serial connection setup
PORT = '/dev/ttyUSB0'
BAUDRATE = 1200

# Global variable for weight deviation threshold
WEIGHT_DEVIATION_THRESHOLD = 0.01
READ_DURATION = 10  # 10seconds


if __name__ == "__main__":
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {PORT} at {BAUDRATE} baud.")
        while True:
            print("\n\n\n")
            sku = input("Enter SKU...\n")
            print("Counting...")
            weight = get_stable_weight(PORT, BAUDRATE, WEIGHT_DEVIATION_THRESHOLD, READ_DURATION)
            if weight:
                calculate_sku_quantity(sku, df, weight)
                time.sleep(3)  # Adjust the delay as necessary for your use case

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')
