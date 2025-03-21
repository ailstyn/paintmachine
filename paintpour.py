import time
import os
import statistics
import RPi.GPIO as GPIO
from hx711 import HX711
from rpi_lcd import LCD
import logging

# Configure logging
logging.basicConfig(filename='paintpour.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#Define GPIO pins for each relay/sensor pair
pairs = [
    {
        'start_button_pin': 16,
        'solenoid': 12,
        'dout_pin': 21,
        'pd_sck_pin': 20,
        'scale_ratio': 13227.143
    },
    {
        'start_button_pin': xx,
        'solenoid': xx,
        'dout_pin': xx,
        'pd_sck_pin': xx,
        'scale_ratio': xx
    },
    {
        'start_button_pin': yy,
        'solenoid': yy,
        'dout_pin': yy,
        'pd_sck_pin': yy,
        'scale_ratio': yy
    },
    {
        'start_button_pin': zz,
        'solenoid': zz,
        'dout_pin': zz,
        'pd_sck_pin': zz,
        'scale_ratio': zz
    }
]

# Assign all the GPIO pins
GPIO.setmode(GPIO.BCM)
start_button_pin = 16
up_button_pin = 6
down_button_pin = 19
set_weight_button_pin = 13
solenoid = 12
pourTimer = 8.00
current_weight = 0
target_weight = 16
tare_button_pin = 26
weight = 0
GPIO.setup(start_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(up_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(down_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(set_weight_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(solenoid, GPIO.OUT)
GPIO.setup(tare_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(solenoid, GPIO.LOW)

# Set up LCD display
lcd = LCD()

# Create scale objects
scale_0 = HX711(dout_pin=pairs[], pd_sck_pin=20)
scale_0.set_scale_ratio(13227.143)

scale_1 = HX711(dout_pin=xx, pd_sck_pin=xx)
scale_1.set_scale_ratio(xx)

scale_2 = HX711(dout_pin=yy, pd_sck_pin=yy)
scale_2.set_scale_ratio(yy)

scale_3 = HX711(dout_pin=zz, pd_sck_pin=zz)
scale_3.set_scale_ratio(zz)



# Weight set function
def set_weight():
    time.sleep(0.5)
    logging.info('set weight function begun')
    global target_weight
    target_weight = current_weight
    lcd.clear()
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
            logging.info('Target weight saved')
            target_weight = round(target_weight, 2)
            lcd.text('TARGET SAVED: ', 1)
            lcd.text(str(target_weight) + " oz", 2)
#            Printouts to check that the variables are working correctly
#            print(target_weight)
#            print(pourTimer)
            time.sleep(3)
            set_time()
            return target_weight, pourTimer
        if not GPIO.input(up_button_pin):           # increase the target weight
            target_weight += 0.1
#            print(target_weight)
            time.sleep(0.3)
        if not GPIO.input(down_button_pin):         # decrease the target weight
            new_target_weight = target_weight - 0.1
            if new_target_weight >= 0:
                target_weight = new_target_weight
#            print(target_weight)
            time.sleep(0.3)

        lcd.text("Target: " + "{:.1f}".format(target_weight), 1)

# Time set funtion
def set_time():
    time.sleep(0.5)
    logging.info('set time function begun')
    global pourTimer
    lcd.clear()
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
#            print('Time saved')
            lcd.text('TARGET SAVED: ', 1)
            lcd.text(str(pourTimer) + " oz", 2)
            time.sleep(3)
            return pourTimer
        if not GPIO.input(up_button_pin):           # increase the target time
            pourTimer += 1
#            print(pourTimer)
            time.sleep(0.3)
        if not GPIO.input(down_button_pin):         # decrease the target time
            new_pourTimer = pourTimer - 1
            if new_pourTimer >= 0:
                pourTimer = new_pourTimer
#            print(pourTimer)
            time.sleep(0.3)

        lcd.text("Target: " + "{:.1f}".format(target_weight), 1)


# Turns on the solenoid and starts reading from the weight sensor,
# when the current weight exceeds or equals the target weight the 
# solenoid is turned off and the function exits
def fill():
    # Small delay to prevent button double-presses
    time.sleep(0.1)
    # Set the initial countdown value (in seconds)
    # pourTimer = target_weight
    time_remaining = pourTimer

    try:
        current_weight = scale.get_weight_mean(3)
    except statistics.StatisticsError:
        logging.error('Error calculating weight, retrying...')
        

    # Check to see if the scale is clear
    if current_weight < target_weight * 0.5:
        scale.zero()
        # Turn on the relay
        GPIO.output(solenoid, GPIO.HIGH)
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
            if current_weight >= target_weight:
                # End the function and return to main loop
                break

            # Calculate the elapsed time and the remaining time
            elapsed_time = time.perf_counter() - start_time
            time_remaining = pourTimer - elapsed_time

            # Print the current weight and countdown value to the LCD display
            lcd.text("Weight: {:.1f}".format(current_weight), 1)
            lcd.text("Time: {:.2f}".format(time_remaining), 2)
            
        # Turn off the relay
        GPIO.output(solenoid, GPIO.LOW)

        # Print a message to the LCD display indicating whether the target weight was reached
        if current_weight >= target_weight:
            lcd.clear()
            lcd.text("Target weight reached!", 1)
            lcd.text("Weight: {:.1f}".format(current_weight), 2)
            time.sleep(1)
            return
        else:
            lcd.clear()
            lcd.text("Time's up!", 1)
            lcd.text("Weight: {:.1f}".format(current_weight), 2)
#            print("Time's up!")
            time.sleep(1)
            return

        # Wait for 2 seconds before returning
        time.sleep(2)
        return
    else:
        lcd.text('CLEAR SCALE', 1)
        logging.info('Weight on scale, fill cancelled')
        return


# Main loop
try:
    lcd.clear()
    scale.zero()
    logging.info('paint filler program loaded')
    while True:
        lcd.text('READY', 1)
        # Displays a live readout of the weight currently on the scale
        weight = round(scale.get_weight_mean(5), 2)
        if weight >= 0 and weight != False:
            lcd.text(str(weight)+' oz', 2)

        # If the set weight button was pressed, execute the set_weight function
        if not GPIO.input(set_weight_button_pin):
            set_weight()

        # If the start button was pressed, execute the fill function
        elif not GPIO.input(start_button_pin):
            fill()
            
        # If the set zero button was pressed, tare the scale
        elif not GPIO.input(tare_button_pin):
            scale.zero()

except KeyboardInterrupt:
    pass
    
finally:
    GPIO.cleanup()
    logging.info('Program terminated and GPIO cleaned up.')