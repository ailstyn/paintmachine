import time
import pigpio
from rpi_lcd import LCD
from hx711 import HX711

# Initialize LCD display
lcd = LCD()
lcd.begin(16, 2)

# Set up GPIO pins for buttons and relay
set_weight_button_pin = 16
start_button_pin = 12
led_pin = 26
up_button_pin = 6
down_button_pin = 13 

pi = pigpio.pi()
pi.set_mode(set_weight_button_pin, pigpio.INPUT)
pi.set_pull_up_down(set_weight_button_pin, pigpio.PUD_DOWN)
pi.set_mode(start_button_pin, pigpio.INPUT)
pi.set_pull_up_down(start_button_pin, pigpio.PUD_DOWN)
pi.set_mode(led_pin, pigpio.OUTPUT)

# Initialize the HX711 class with the appropriate pins and calibration value
scale = HX711(gpio)

# Global variables
target_weight = 0.0
pourTimer = 0.0

def set_weight():
    time.sleep(0.5)
    print('set weight function begun')
    global target_weight
    target_weight = scale.read()
    lcd.clear()
    button_pressed = False
    increment = 0.1
    increment_state = 0
    last_press_time = time.time()

    while True:
        up_pressed = not pi.read(up_button_pin)
        down_pressed = not pi.read(down_button_pin)

        if not button_pressed and up_pressed:
            button_pressed = True
            last_press_time = time.time()
        elif button_pressed and not up_pressed:
            button_pressed = False
            increment_state = 0

        if not button_pressed and down_pressed:
            button_pressed = True
            last_press_time = time.time()
        elif button_pressed and not down_pressed:
            button_pressed = False
            increment_state = 0

        if up_pressed or down_pressed:
            current_time = time.time()
            elapsed_time = current_time - last_press_time

            if elapsed_time >= 3 and elapsed_time < 6 and increment_state == 0:
                increment_state = 1
                increment = 1
            elif elapsed_time >= 6 and increment_state == 1:
                increment_state = 2
                increment = 10

            if up_pressed:
                target_weight += increment
            if down_pressed:
                new_target_weight = target_weight - increment
                if new_target_weight >= 0:
                    target_weight = new_target_weight

            time.sleep(0.1)

        if not button_pressed and not GPIO.input(set_weight_button_pin):
            button_pressed = True
        elif button_pressed and GPIO.input(set_weight_button_pin):
            print('Target weight saved')
            target_weight = round(target_weight, 2)
            lcd.text('TARGET SAVED: ', 1)
            lcd.text(str(target_weight) + " oz", 2)
            time.sleep(3)
            set_time()
            return

        lcd.text("Target: {:.1f}".format(target_weight), 1)


def set_time():
    time.sleep(0.5)
    print('set time function begun')
    global pourTimer
    pourTimer = target_weight
    lcd.clear()
    button_pressed = False
    while True:
        if not button_pressed and pi.read(set_weight_button_pin) == 1:
            button_pressed = True
        elif button_pressed and pi.read(set_weight_button_pin) == 0:
            print('Pour time saved')
            pourTimer = round(pourTimer, 2)
            lcd.text('POUR TIME SAVED: ', 1)
            lcd.text(str(pourTimer) + " sec", 2)
            time.sleep(3)
            return
        if not pi.read(up_button_pin):
            print('up button pressed')
            pourTimer += 0.1
            time.sleep(0.1)
        if not pi.read(down_button_pin):
            print('down button pressed')
            new_pour_time = pourTimer - 0.1
            if new_pour_time >= 0:
                pourTimer = new_pour_time
            time.sleep(0.1)

        lcd.text("Pour Time: {:.1f}".format(pourTimer), 1)

def check_weight():
    time.sleep(0.1)
    time_remaining = pourTimer

    if scale.read() < target_weight * 0.1:
        scale.zero()
        pi.write(led_pin, 1)
        print('relay ON')

        start_time = time.perf_counter()
        print('start time SET')

        while time_remaining > 0:
            current_weight = scale.read()
            if current_weight >= target_weight:
                break

            elapsed_time = time.perf_counter() - start_time
            time_remaining = pourTimer - elapsed_time

            lcd.text("Weight: {:.1f}".format(current_weight), 1)
            lcd.text("Time: {:.2f}".format(time_remaining), 2)

            print("pourTimer: {:.3f}".format(pourTimer))
            print("Elapsed time: {:.3f}".format(elapsed_time))
            print("Time remaining: {:.3f}".format(time_remaining))

        pi.write(led_pin, 0)
        lcd.text("Target Weight Reached", 1)
        print('relay OFF')

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
            time.sleep(1)
            return

        time.sleep(2)
        return
    else:
        lcd.text('CLEAR SCALE', 1)
        return

try:
    lcd.clear()
    scale.zero()
    print('paint filler program loaded')

    while True:
        lcd.text('READY', 1)
        current_weight = scale.read()
        lcd.text(str(current_weight) + ' g', 2)
        time.sleep(0.1)

        if pi.read(set_weight_button_pin) == 1:
            set_weight()

        elif pi.read(start_button_pin) == 1:
            check_weight()

except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
    pi.stop()
