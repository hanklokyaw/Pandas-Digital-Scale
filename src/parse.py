import re
import time
import serial
from PIL import Image, ImageDraw, ImageFont


# # Function to read CSV and return the weight for a given SKU
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


# # Function to parse and decode the weight from a line
def parse_weight(raw_line):
    try:
        # Ensure raw_line is a string
        if isinstance(raw_line, bytes):
            line = raw_line.decode('ascii', errors='ignore').strip()
        else:
            line = raw_line.strip()

        # Extract the weight using regex
        match = re.search(r'([+-]?\d+\.\d+)', line)
        if match:
            weight_str = match.group(1)
            return float(weight_str)
    except Exception as e:
        print(f"Decoding error: {e}")
    return None


# Function to calculate the deviation in weight readings
def calculate_deviation(weight_readings):
    if len(weight_readings) < 3:
        return float('inf')  # If there are fewer than 5 readings, deviation is high
    return max(weight_readings) - min(weight_readings)


# Function to reset weight readings if the interval exceeds 5 seconds
def reset_timer_if_exceeded(start_time, weight_readings):
    current_time = time.time()
    if current_time - start_time > 3:
        weight_readings.clear()  # Reset readings list
        print("Stable weight not detected within 5 seconds, restarting...")
        return current_time  # Reset start time
    return start_time


# Stable weight detection logic
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
                    if len(weight_readings) >= 3:
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


def calculate_sku_quantity(sku, df, total_weight):
    """
    Use a QR Code Scanner to scan the weight and calculate the number of pieces.
    """
    item_weight, bin_weight = get_weight_by_sku(sku, df)
    if item_weight is not None:
        quantity = round((total_weight - bin_weight) / item_weight)
        print(f"Total weight: {total_weight:.2f} grams. Approximate quantity: {quantity} pieces.")
        return quantity
        time.sleep(8)
    else:
        # lcd_display("NOTIFICATION","SKU NOT FOUND!","PLEASE CHECK CSV.","")
        print("SKU not found in the database. Please check and try again.")
        return None


def oled_display(disp, line1, line2):
    # Create a blank image and draw object
    image = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)

    # Define fonts (adjust the path to Font.ttc if necessary)
    # Load the 6x12 bitmap font
    font1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)

    # Draw text
    draw.text((10, 0), line1[:12], font=font1, fill=0)  # First line
    draw.text((10, 15), line1[12:24], font=font1, fill=0)  # Second line (2 lines)
    draw.text((10, 31), line1[24:36], font=font1, fill=0)
    draw.text((10, 45), line2[:10], font=font2, fill=0)

    # Add spacing before status
    # draw.text((10, 70), status[:7].upper(), font=font1, fill=0) # Status line

    # Rotate if needed and display
    image = image.rotate(180)
    disp.ShowImage(disp.getbuffer(image))
