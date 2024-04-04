import time
import RPi.GPIO as GPIO
from hx711 import HX711
GPIO.setmode(GPIO.BCM)

# Create scale object
scale = HX711(dout_pin=21, pd_sck_pin=20)
scale.set_scale_ratio()
scale.zero()
calib = float(input("enter weight and press enter when ready"))
meani = []
resultacc = []
resultprec = []
resulttime = []

try:
    for i in range(1, 6):
        input(f"Taking 100 readings at increments of {i} and finding the range of outputs. Press enter when ready")
        meani.clear()
        
        start_time = time.perf_counter()
        for i in range (1, 101):
            meani.append(scale.get_weight_mean(i))
        elapsed_time = time.perf_counter() - start_time
        resulttime.append(elapsed_time)
        
        maxi = max(meani)
        mini = min(meani)
        avgi = sum(meani)/len(meani)
        
        prec = ((maxi - mini) / calib) * 100
        resultprec.append(prec)
        
        acc = (avgi / calib) * 100
        resultacc.append(acc)
        
        print(f"The highest value with mean {i} is {maxi}")
        print(f"The lowest value with mean {i} is {mini}")
        print(f"The deviation was {prec}%")
        print(f"The accuracy was {acc}%")
        print(f"The operation took {elapsed_time} seconds.")
        
    resulttime0 = resulttime(0)
    resulttime1 = resulttime(1)
    resulttime2 = resulttime(2)
    resulttime3 = resulttime(3)
    
    resultprec0 = resultprec(0)
    resultprec1 = resultprec(1)
    resultprec2 = resultprec(2)
    resultprec3 = resultprec(3)
    
    resultacc0 = resultacc(0)
    resultacc1 = resultacc(1)
    resultacc2 = resultacc(2)
    resultacc3 = resultacc(3)
    
    print(f"The mean 5 method took {resulttime0}, had a deviation of {resultprec0}%, and accuracy of {resultacc0}")
    print(f"The mean 10 method took {resulttime1}, had a deviation of {resultprec1}%, and accuracy of {resultacc1}") 
    print(f"The mean 15 method took {resulttime2}, had a deviation of {resultprec2}%, and accuracy of {resultacc2}")
    print(f"The mean 20 method took {resulttime3}, had a deviation of {resultprec3}%, and accuracy of {resultacc3}")
     
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
