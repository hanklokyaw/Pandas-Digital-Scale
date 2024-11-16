import re
import time
import pandas as pd
import serial

# Function to read CSV and return the weight for a given SKU
def get_weight_by_sku(sku, dataframe):
    # Filter the DataFrame for the provided SKU
    result = dataframe[dataframe['SKU'] == sku]

    if not result.empty:
        # If the SKU is found, return the weight
        item_weight = result['ItemWeight'].values[0]
        bin_weight = result['BinWeight'].values[0]
        return item_weight, bin_weight
    else:
        # Return a message if SKU not found
        return None, None

# Function to parse and decode the weight from a line
def parse_weight(raw_line):
    try:
        line = raw_line.decode('ascii', errors='ignore').strip()
        # print(f"Received: {line}")
        match = re.search(r'([+-]?\d+\.\d+)', line)
        if match:
            weight_str = match.group(1)
            return float(weight_str)
    except Exception as e:
        print(f"Decoding error: {e}")
    return None


# Function to calculate the deviation in weight readings
def calculate_deviation(weight_readings):
    if len(weight_readings) < 5:
        return float('inf')  # If there are fewer than 5 readings, deviation is high
    return max(weight_readings) - min(weight_readings)


# Function to reset weight readings if the interval exceeds 5 seconds
def reset_timer_if_exceeded(start_time, weight_readings):
    current_time = time.time()
    if current_time - start_time > 5:
        weight_readings.clear()  # Reset readings list
        print("Stable weight not detected within 5 seconds, restarting...")
        return current_time  # Reset start time
    return start_time


def calculate_sku_quantity(sku, df, total_weight):
    """
    Use a QR Code Scanner to scan the weight and calculate the number of pieces.
    """
    item_weight, bin_weight, = get_weight_by_sku(sku, df)
    if item_weight is not None:
        quantity = round((total_weight - bin_weight) / item_weight)
        # lcd_display("RESULT: ","",f"{sku}",f"QTY: {quantity}PCS")
        print(f"Total weight: {total_weight:.2f} grams. Approximate quantity: {quantity} pieces.")
        time.sleep(8)
    else:
        # lcd_display("NOTIFICATION","SKU NOT FOUND!","PLEASE CHECK CSV.","")
        print("SKU not found in the database. Please check and try again.")



def get_stable_weight(port, baudrate, threshold, read_duration):
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        weight_readings = []
        start_time = time.time()

        while True:
            # Read and parse weight from scale
            if ser.in_waiting > 0:
                raw_line = ser.readline()
                weight = parse_weight(raw_line)

                if weight is not None:
                    if weight < 5.0:
                        print("Please place your bin.")
                        weight_readings.clear()
                        start_time = time.time()
                        continue  # Wait for a valid weight to begin

                    # Add reading to list and maintain only last 5 seconds of readings
                    weight_readings.append((weight, time.time()))
                    weight_readings = [(w, t) for w, t in weight_readings if t >= time.time() - read_duration]
                    # print([w for w, t in weight_readings])  # Show readings for debugging

                    # Check if we have 5 readings and stability
                    if len(weight_readings) >= 5:
                        deviation = calculate_deviation([w for w, t in weight_readings])
                        if deviation < threshold:
                            print(f"Stable weight detected: {weight:.3f}")
                            return weight

    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()