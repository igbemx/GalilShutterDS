import PyTango
import time

dev = PyTango.DeviceProxy('test/galil_shutter/1')
camera = PyTango.DeviceProxy('B318A-E/dia/andor-zyla-01')

print(dev.abs_position)


for i in range(100):
    #print('Open')
    dev.Open()
    time.sleep(0.023)
    #camera.SoftwareTrigger()
    #print('Close')
    dev.Close()
    time.sleep(0.023)
    print(i)