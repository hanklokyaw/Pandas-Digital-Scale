import re
import time
import serial
from PIL import Image, ImageDraw, ImageFont

# Function to read CSV and return the weight for a given SKU
def get_weight_by_sku(sku, dataframe):
    """
    Retrieve the item and bin weights for a given SKU from the dataframe.

    Args:
        sku (str): The SKU identifier.
        dataframe (DataFrame): Pandas DataFrame containing SKU data with 'SKU', 'ItemWeight', and 'BinWeight' columns.

    Returns:
        tuple: Item weight and bin weight if the SKU is found; otherwise, (None, None).
    """
    result = dataframe[dataframe['SKU'] == sku]
    if not result.empty:
        item_weight = result['ItemWeight'].values[0]
        bin_weight = result['BinWeight'].values[0]
        return item_weight, bin_weight
    else:
        return None, None


# Function to parse and decode the weight from a line
def parse_weight(raw_line):
    """
    Extract weight value from the serial input using regex.

    Args:
        raw_line (bytes/str): Raw data read from the scale.

    Returns:
        float: Parsed weight value if successfully extracted; otherwise, None.
    """
    try:
        if isinstance(raw_line, bytes):
            line = raw_line.decode('ascii', errors='ignore').strip()
        else:
            line = raw_line.strip()

        match = re.search(r'([+-]?\d+\.\d+)', line)
        if match:
            return float(match.group(1))
    except Exception as e:
        print(f"Decoding error: {e}")
    return None


# Function to calculate the deviation in weight readings
def calculate_deviation(weight_readings):
    """
    Compute the difference between the maximum and minimum weights in the readings.

    Args:
        weight_readings (list): List of weight readings.

    Returns:
        float: Deviation in the weight readings.
    """
    if len(weight_readings) < 3:
        return float('inf')  # High deviation if fewer than 3 readings
    return max(weight_readings) - min(weight_readings)


# Function to reset weight readings if the interval exceeds the threshold
def reset_timer_if_exceeded(start_time, weight_readings):
    """
    Reset the timer and clear weight readings if time exceeds the threshold.

    Args:
        start_time (float): Timestamp of the last valid reading.
        weight_readings (list): List of recorded weight readings.

    Returns:
        float: Updated start time.
    """
    current_time = time.time()
    if current_time - start_time > 3:
        weight_readings.clear()
        print("Stable weight not detected within 5 seconds, restarting...")
        return current_time
    return start_time


# Function to detect stable weight
def get_stable_weight(port, baudrate, threshold, read_duration):
    """
    Detect stable weight from the scale within the specified duration.

    Args:
        port (str): Serial port connected to the scale.
        baudrate (int): Baud rate for the serial connection.
        threshold (float): Maximum allowable deviation for stable weight.
        read_duration (int): Time window to consider for readings.

    Returns:
        float: Stable weight value if detected; otherwise, None.
    """
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        weight_readings = []
        start_time = time.time()

        while True:
            if ser.in_waiting > 0:
                raw_line = ser.readline()
                weight = parse_weight(raw_line)

                if weight is not None:
                    if weight < 5.0:
                        print("Please place your bin.")
                        weight_readings.clear()
                        start_time = time.time()
                        continue

                    weight_readings.append((weight, time.time()))
                    weight_readings = [(w, t) for w, t in weight_readings if t >= time.time() - read_duration]

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


# Function to calculate SKU quantity
def calculate_sku_quantity(sku, df, total_weight):
    """
    Calculate the number of items based on total weight and SKU-specific weights.

    Args:
        sku (str): SKU identifier.
        df (DataFrame): Pandas DataFrame containing SKU weights.
        total_weight (float): Measured total weight.

    Returns:
        int: Calculated quantity of items if SKU is found; otherwise, None.
    """
    item_weight, bin_weight = get_weight_by_sku(sku, df)
    if item_weight is not None:
        quantity = round((total_weight - bin_weight) / item_weight)
        print(f"Total weight: {total_weight:.2f} grams. Approximate quantity: {quantity} pieces.")
        return quantity
    else:
        print("SKU not found in the database. Please check and try again.")
        return None


# Function to display text on the OLED screen
def oled_display(disp, line1, line2):
    """
    Display text on the OLED screen.

    Args:
        disp (object): OLED display instance.
        line1 (str): Text for the first line.
        line2 (str): Text for the second line.
    """
    image = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)

    font1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)

    draw.text((10, 0), line1[:12], font=font1, fill=0)
    draw.text((10, 15), line1[12:24], font=font1, fill=0)
    draw.text((10, 31), line1[24:36], font=font1, fill=0)
    draw.text((10, 45), line2[:10], font=font2, fill=0)

    image = image.rotate(180)
    disp.ShowImage(disp.getbuffer(image))


# Function to check sku before counting
def check_sku(df, sku):
    if len(df[df['SKU']==sku]) > 0:
        return True
    else:
        return False
