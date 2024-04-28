import time
import os
import RPi.GPIO as GPIO
from hx711 import HX711
from rpi_lcd import LCD

# Assign all the GPIO pins
GPIO.setmode(GPIO.BCM)
start_button_pin = 12
up_button_pin = 6
down_button_pin = 13
set_weight_button_pin = 16
solenoid = 26
pourTimer = 8.00
current_weight = 0
target_weight = 16
GPIO.setup(start_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(up_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(down_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(set_weight_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(solenoid, GPIO.OUT)
GPIO.output(solenoid, GPIO.LOW)

# Set up LCD display
#lcd = LCD()

# Create scale object
scale = HX711(dout_pin=21, pd_sck_pin=20)
scale.set_scale_ratio(13227.143)

# Weight set function
def set_weight():
    time.sleep(0.5)
    print('set weight function begun')
    global target_weight
    target_weight = current_weight
#    lcd.clear()
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
            print('Target weight saved')
            target_weight = round(target_weight, 2)
#            lcd.text('TARGET SAVED: ', 1)
#            lcd.text(str(target_weight) + " oz", 2)
            time.sleep(3)
            set_time()
            return target_weight, pourTimer
        if not GPIO.input(up_button_pin):           # increase the target weight
            print('up button pressed')
            target_weight += 0.1
            time.sleep(0.1)
        if not GPIO.input(down_button_pin):         # decrease the target weight
            print('down button pressed')
            new_target_weight = target_weight - 0.1
            if new_target_weight >= 0:
                target_weight = new_target_weight
            time.sleep(0.1)

#        lcd.text("Target: " + "{:.1f}".format(target_weight), 1)

# Time set funtion
def set_time():
    time.sleep(0.5)
    print('set time function begun')
    #global pourTimer
#    lcd.clear()
    button_pressed = False
    while True:
        if not button_pressed and not GPIO.input(set_weight_button_pin):
            # If the button hasn't been pressed yet and it's currently being pressed, set the flag to True
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            # If the button has been pressed and it's currently being released, save the target weight and return
            print('Time saved')
 #           lcd.text('TARGET SAVED: ', 1)
 #           lcd.text(str(pourTimer) + " oz", 2)
            time.sleep(3)
            return pourTimer
        if not GPIO.input(up_button_pin):           # increase the target time
            print('up button pressed')
            pourTimer += 1
            time.sleep(0.1)
        if not GPIO.input(down_button_pin):         # decrease the target time
            print('down button pressed')
            new_pourTimer = pourTimer - 1
            if new_pourTimer >= 0:
                pourTimer = new_pourTimer
            time.sleep(0.1)

#        lcd.text("Target: " + "{:.1f}".format(target_weight), 1)


# Turns on the solenoid and starts reading from the weight sensor,
# when the current weight exceeds or equals the target weight the 
# solenoid is turned off and the function exits
def check_weight():
    # Small delay to prevent button double-presses
    time.sleep(0.1)
    # Set the initial countdown value (in seconds)
    # pourTimer = target_weight
    time_remaining = pourTimer


    # Check to see if the scale is clear
    if scale.get_weight_mean(5) < target_weight * 0.1:
        scale.zero()
        # Turn on the relay
        GPIO.output(solenoid, GPIO.HIGH)
        print('relay ON')

        # Get the start time
        start_time = time.perf_counter()
        print('start time SET')

        # Loop until the countdown reaches 0 or the current weight is greater than or equal to the target weight
        while time_remaining > 0:
            # Get the current weight from the scale
            current_weight = scale.get_weight_mean(3)
            # Check if the current weight is greater than or equal to the target weight
            if current_weight >= target_weight:
                # End the function and return to main loop
                break

            # Calculate the elapsed time and the remaining time
            elapsed_time = time.perf_counter() - start_time
            time_remaining = pourTimer - elapsed_time

            # Print the current weight and countdown value to the LCD display
#            lcd.text("Weight: {:.1f}".format(current_weight), 1)
#            lcd.text("Time: {:.2f}".format(time_remaining), 2)
            
            # Print debug messages to confirm the values of countdown, elapsed_time, and time_remaining
#            print("pourTimer: {:.3f}".format(pourTimer))
#            print("Elapsed time: {:.3f}".format(elapsed_time))
            print("Time remaining: {:.3f}".format(time_remaining))
            print(current_weight)
        # Turn off the relay
        GPIO.output(solenoid, GPIO.LOW)
#        lcd.text("Target Weight Reached", 1)
        print('relay OFF')

        # Print a message to the LCD display indicating whether the target weight was reached
        if current_weight >= target_weight:
#            lcd.clear()
#            lcd.text("Target weight reached!", 1)
            print("Target weight reached!")
#            lcd.text("Weight: {:.1f}".format(current_weight), 2)
            time.sleep(1)
            return
        else:
#            lcd.clear()
#            lcd.text("Time's up!", 1)
#            lcd.text("Weight: {:.1f}".format(current_weight), 2)
            print("Time's up!")
            time.sleep(1)
            return

        # Wait for 2 seconds before returning
        time.sleep(2)
        return
    else:
#        lcd.text('CLEAR SCALE', 1)
        print('CLEAR SCALE')
        return
# Load scale calibration files
#try:
#swap_file_name = 'swap_file.swp'
#if os.path.isfile(swap_file_name):
#    with open(swap_file_name, 'rb') as swap_file:
#        scale = pickle.load(swap_file)

# Main loop
try:
#    lcd.clear()
    scale.zero()
    print('paint filler program loaded')
    while True:
#        lcd.text('READY', 1)
#        lcd.text(str(scale.get_data_mean(3))+' g', 2)
        weight = scale.get_weight_mean(5)
        if weight >= 0 and weight != False:
            print(weight)
#        time.sleep(0.1)

        # If the set weight button was pressed, execute the set_weight function
        if not GPIO.input(set_weight_button_pin):
            set_weight()

        # If the start button was pressed, execute the check_weight function
        elif not GPIO.input(start_button_pin):
            check_weight()

except KeyboardInterrupt:
    pass
    
finally:
    GPIO.cleanup()
