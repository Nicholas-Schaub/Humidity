import os
import sys
path = os.path.realpath(__file__).replace(__file__,'..')
sys.path.append(path)

from Humidity.RHUtilities import RHSensor
import Adafruit_DHT
import time

class DHT_Reader(RHSensor):
	
	_sensor_types = [Adafruit_DHT.AM2302,
					 Adafruit_DHT.DHT11,
					 Adafruit_DHT.DHT22]
		
	def __init__(self,pin,period,sensor):
		if sensor not in self._sensor_types:
			KeyError("The sensor indicated is invalid for this class.")
		self._sensor = sensor
		self.period = period
		self._pin = pin
		
		# Set data categories and units
		self.data_categories = ['Time','Temperature','Relative Humidity']
		self._data_units = ['s','C','%']
		
	def _read_sensor(self):
		result = {}
		result['Relative Humidity'], result['Temperature'] = Adafruit_DHT.read_retry(
															 self._sensor,
															 self._pin,
															 delay_seconds=0.5)
		result['Time'] = time.time()
		
		return result
		
class AM2302(DHT_Reader):
	is_rh_sensor = True
	
	def __init__(self,pin=4,period=2):
		super(AM2302,self).__init__(pin,period,Adafruit_DHT.AM2302)
		
class DHT11(DHT_Reader):
	is_rh_sensor = True
	
	def __init__(self,pin=4,period=2):
		super(DHT11,self).__init__(pin,period,Adafruit_DHT.DHT11)
		
class DHT22(DHT_Reader):
	is_rh_sensor = True
	
	def __init__(self,pin=4,period=2):
		super(DHT22,self).__init__(pin,period,Adafruit_DHT.DHT22)

if __name__=='__main__':
	reader = AM2302(4,1)
	print(reader.is_rh_sensor)
	reader.print_console(True)
	reader.start_continuous_read()
