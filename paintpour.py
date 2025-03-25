import time
import os
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711
import logging
import sys
from PyQt5.QtWidgets import QApplication
from paintgui import MainWindow
from multiprocessing import Process

# Configure logging
logging.basicConfig(filename='paintpour.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Filepath for saving/loading settings
settings_file = 'settings.txt'

# Function to load settings from file
def load_settings():
    global pourTimer, target_weight, scale_1_ratio, scale_2_ratio, scale_3_ratio, scale_4_ratio
    try:
        with open(settings_file, 'r') as file:
            lines = file.readlines()
            pourTimer = float(lines[0].strip())
            target_weight = float(lines[1].strip())
            scale_1_ratio = float(lines[2].strip())
            scale_2_ratio = float(lines[3].strip())
            scale_3_ratio = float(lines[4].strip())
            scale_4_ratio = float(lines[5].strip())
    except FileNotFoundError:
        logging.warning('Settings file not found. Using default values.')
    except Exception as e:
        logging.error(f'Error loading settings: {e}')

# Function to save settings to file
def save_settings():
    global pourTimer, target_weight, scale_1_ratio, scale_2_ratio, scale_3_ratio, scale_4_ratio
    try:
        with open(settings_file, 'w') as file:
            file.write(f'{pourTimer}\n')
            file.write(f'{target_weight}\n')
            file.write(f'{scale_1_ratio}\n')
            file.write(f'{scale_2_ratio}\n')
            file.write(f'{scale_3_ratio}\n')
            file.write(f'{scale_4_ratio}\n')
    except Exception as e:
        logging.error(f'Error saving settings: {e}')

# Assign all the GPIO pins
GPIO.setmode(GPIO.BCM)

# Start button pins
startB1 = 16
startB2 = 0
startB3 = 0
startB4 = 0

# Relay pins
relay1 = 12
relay2 = 0
relay3 = 0
relay4 = 0

# Remaining button pins
tare_button_pin = 26
up_button_pin = 6
down_button_pin = 19
set_weight_button_pin = 13

# Create variables for the weight and current weight so the program doesn't have a fit
current_weight = 0
weight = 0

# Load settings on startup
load_settings()

# Set up the GPIO pins
GPIO.setup(up_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(down_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(set_weight_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(tare_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(startB1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(startB2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(startB3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(startB4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Start all the relays LOW so they don't accidentally turn on
GPIO.setup(relay1, GPIO.LOW)
GPIO.setup(relay2, GPIO.LOW)
GPIO.setup(relay3, GPIO.LOW)
GPIO.setup(relay4, GPIO.LOW)

# Create scale objects
scale_1 = HX711(dout_pin=21, pd_sck_pin=20)
scale_1.set_scale_ratio(scale_1_ratio)

scale_2 = HX711(dout_pin=xx, pd_sck_pin=xx)
scale_2.set_scale_ratio(scale_2_ratio)

scale_3 = HX711(dout_pin=yy, pd_sck_pin=yy)
scale_3.set_scale_ratio(scale_3_ratio)

scale_4 = HX711(dout_pin=zz, pd_sck_pin=zz)
scale_4.set_scale_ratio(scale_4_ratio)

# Flags to track the status of each relay/scale pair
relay1_in_use = False
relay2_in_use = False
relay3_in_use = False
relay4_in_use = False

# Function to update GUI
def update_gui(current_weight, time_remaining):
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(str(current_weight) + " oz", "Time Remaining: " + str(time_remaining) + "s")
    sys.exit(app.exec_())

# Weight set function
def set_weight():
    time.sleep(0.5)
    logging.info('set weight function begun')
    global target_weight
    target_weight = current_weight
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
            logging.info('Target weight saved')
            target_weight = round(target_weight, 2)
            time.sleep(3)
            set_time()
            return target_weight, pourTimer
        if not GPIO.input(up_button_pin):           # increase the target weight
            target_weight += 0.1
            time.sleep(0.3)
        if not GPIO.input(down_button_pin):         # decrease the target weight
            new_target_weight = target_weight - 0.1
            if new_target_weight >= 0:
                target_weight = new_target_weight
            time.sleep(0.3)

# Time set funtion
def set_time():
    time.sleep(0.5)
    logging.info('set time function begun')
    global pourTimer
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
            logging.info('Target time saved', pourTimer)
            time.sleep(3)
            return pourTimer
        if not GPIO.input(up_button_pin):           # increase the target time
            pourTimer += 1
            time.sleep(0.3)
        if not GPIO.input(down_button_pin):         # decrease the target time
            new_pourTimer = pourTimer - 1
            if new_pourTimer >= 0:
                pourTimer = new_pourTimer
            time.sleep(0.3)

# Function to handle multiprocessing
def start_fill_process(relay, scale, relay_in_use_flag):
    global relay1_in_use, relay2_in_use, relay3_in_use, relay4_in_use
    if not relay_in_use_flag:
        relay_in_use_flag = True
        p = Process(target=fill, args=(relay, scale, relay_in_use_flag))
        p.start()
    else:
        logging.info(f'Relay {relay} is already in use.')

# Turns on the solenoid and starts reading from the weight sensor,
# when the current weight exceeds or equals the target weight the 
# solenoid is turned off and the function exits
def fill(relay, scale, relay_in_use_flag):
    global relay1_in_use, relay2_in_use, relay3_in_use, relay4_in_use
    # Small delay to prevent button double-presses
    time.sleep(0.1)
    # Set the initial countdown value (in seconds)
    time_remaining = pourTimer

    try:
        current_weight = scale.get_weight_mean(3)
    except statistics.StatisticsError:
        logging.error('Error calculating weight, retrying...')

    # Check to see if the scale is clear
    if current_weight < target_weight * 0.5:
        scale.zero()
        GPIO.output(relay, GPIO.HIGH)
        logging.info('relay ON')

        # Get the start time
        start_time = time.perf_counter()

        # Loop until the countdown reaches 0 or the current weight is greater than or equal to the target weight
        while time_remaining > 0:
            # Get the current weight from the scale
            # If the scale returns a statistical error it retries
            try:
                current_weight = scale.get_weight_mean(3)
            except statistics.StatisticsError:
                logging.error('Error calculating weight, retrying...')
                continue
            # Check if the current weight is greater than or equal to the target weight
            # if so, end the loop
            if current_weight >= target_weight:
                break

            # Adjust the elapsed time
            elapsed_time = time.perf_counter() - start_time
            time_remaining = pourTimer - elapsed_time

            # Update the GUI with the current weight and countdown value
            update_gui(current_weight, time_remaining)
            
        # Turn off the relay
        GPIO.output(relay, GPIO.LOW)  # Renamed from solenoid

        # Print a message to the LCD display indicating whether the target weight was reached
        if current_weight >= target_weight:
            lcd.clear()
            lcd.text("Target weight reached!", 1)
            lcd.text("Weight: {:.1f}".format(current_weight), 2)
            time.sleep(1)
        else:
            lcd.clear()
            lcd.text("Time's up!", 1)
            lcd.text("Weight: {:.1f}".format(current_weight), 2)
            time.sleep(1)

        # Wait for 2 seconds before returning
        time.sleep(2)
    else:
        lcd.text('CLEAR SCALE', 1)
        logging.info('Weight on scale, fill cancelled')

    # Clear the relay in use flag
    relay_in_use_flag = False

# Main loop
try:
    scale_1.zero()
    logging.info('paint filler program loaded')
    app = QApplication(sys.argv)
    window = MainWindow("0 oz", "Time Remaining: 0s")
    while True:
        # Displays a live readout of the weight currently on the scale
        weight = round(scale_1.get_weight_mean(5), 2)
        if weight >= 0 and weight != False:
            window.update_labels(str(weight) + ' oz', "Time Remaining: 0s")
            app.processEvents()

        # If the set weight button was pressed, execute the set_weight function
        if not GPIO.input(set_weight_button_pin):
            set_weight()

        # If the start button was pressed, execute the fill function in a new process
        elif not GPIO.input(startB1):  # Renamed from start_button_pin
            start_fill_process(relay1, scale_1, relay1_in_use)
        elif not GPIO.input(startB2):
            start_fill_process(relay2, scale_2, relay2_in_use)
        elif not GPIO.input(startB3):
            start_fill_process(relay3, scale_3, relay3_in_use)
        elif not GPIO.input(startB4):
            start_fill_process(relay4, scale_4, relay4_in_use)
            
        # If the set zero button was pressed, tare the scale
        elif not GPIO.input(tare_button_pin):
            scale_1.zero()

except KeyboardInterrupt:
    pass
    
finally:
    save_settings()  # Save settings on exit
    GPIO.cleanup()
    logging.info('Program terminated and GPIO cleaned up.')