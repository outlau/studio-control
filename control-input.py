import sys
import usb.core
import usb.util
import RPi.GPIO as GPIO

outputs = [GPIO.LOW,GPIO.HIGH]
vals = [43,20,26,8,21]
output_state = [1,1,0,1,0]
pins = [21,20,16,12,17]

holding_down={43:0,20:0,26:0,8:0,21:0}

def analyze_data(data_input):
	for i in data_input:
		try:	
			index = vals.index(i)
			if holding_down[i] == 0:	
				output_state[index] = (output_state[index]+1)%2
				GPIO.output(pins[index],output_state[index])
		except ValueError:
			print "not in array"
	for i in vals:
		if i in data_input:
			holding_down[i] = 1
		else:
			holding_down[i] = 0
	
	print output_state
			
i = 0
for v in pins:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(v,GPIO.OUT)
	GPIO.output(v,output_state[i])
	i += 1


VENDOR_ID = 0x1532
PRODUCT_ID = 0x0201

dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
#print "dev ", dev
#print "confug", dev.bLength

for cfg in dev:
    sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
    for intf in cfg:
        sys.stdout.write('\t' + \
                         str(intf.bInterfaceNumber) + \
                         ',' + \
                         str(intf.bAlternateSetting) + \
                         '\n')
        for ep in intf:
            sys.stdout.write('\t\t' + \
                             str(ep.bEndpointAddress) + \
                             '\n')
                             
interface = 0
endpoint = dev[0][(0,0)][0]

if dev.is_kernel_driver_active(interface) is True:
  # tell the kernel to detach
  dev.detach_kernel_driver(interface)
  # claim the device
  usb.util.claim_interface(dev, interface)

while True:
    try:
        data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
        analyze_data(data)
    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue
# release the device
usb.util.release_interface(dev, interface)
# reattach the device to the OS kernel
dev.attach_kernel_driver(interface)
