import machine
import time
import math


#resistor is 10000
    
def temp():
    
    
    adc_pin = machine.ADC(28)
    R = adc_pin.read_u16()
    RRef = 35400
    TempRefK = 295.15
    B = 1765.5
    
    
    TempK = 1/(1/TempRefK+(1/B)*math.log(R/RRef))
    TempC = TempK - 273.15
    
    print(TempC)
    return TempC
    
