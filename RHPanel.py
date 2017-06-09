import os
import sys
path = os.path.realpath(__file__).replace(__file__,'..')
sys.path.append(path)

import Tkinter as tk
import tkMessageBox
from tkFileDialog import asksaveasfilename
import ttk
import Humidity
import pkgutil
import time
import pyclbr
import Humidity.Settings as settings
from importlib import import_module
import csv
import RPi.GPIO as GPIO

class RHPanel(tk.Frame):
	def __init__(self,master=None,rh_sensor=None):
		
		settings.openCfg()
		
		tk.Frame.__init__(self,master)
		self.pack()
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		
		# Object variables
		self.fullTitle = "Relative Humidity & Temperature"
		self.shortTitle = "RH & Temp"
		self.cfgTitle = "RHTEMP"
		self._humidifier_dc=100
		self._humidifier_pin = 20
		
		master.wm_title(self.shortTitle)
		
		# Selection frame for humidity sensor
		self.sensor_adapter = None
		self._sensors = {"None": None}
		
		prefix = Humidity.__name__+"."
		sensor_adapters = ["None"]
		for importer, modname, ispkg in pkgutil.iter_modules(Humidity.__path__,prefix):
			print(modname)
			module_info = pyclbr.readmodule(modname)
			for mod in module_info.values():
				print(mod.name)
				try:
					m = import_module(modname)
					cl = getattr(m,mod.name)
					print(cl)
					if cl.is_rh_sensor:
						sensor_adapters.append(mod.name)
						self._sensors[mod.name] = modname
				except:
					continue
			
		self._sensorSelectFrame = ttk.LabelFrame(self,text="Select Sensor")
		self._sensorSelectFrame.pack(padx=5,pady=5,fill=tk.BOTH)
		tk.Grid.columnconfigure(self._sensorSelectFrame,0,weight=1)
		tk.Grid.columnconfigure(self._sensorSelectFrame,1,weight=1)
		
		self._sensorSelectVar = tk.StringVar()
		self._sensorSelectVar.set(settings.getCfg(self.cfgTitle,"rh_sensor_class"))
		self._sensorLabel = ttk.Label(self._sensorSelectFrame,
									  text="Select Sensor: ",
									  anchor=tk.E)
		self._sensorLabel.grid(row=0,column=0,sticky=tk.E+tk.W)
		self._sensorSelectMenu = ttk.OptionMenu(self._sensorSelectFrame,
												self._sensorSelectVar,
												self._sensorSelectVar.get(),
												*sensor_adapters)
		self._sensorSelectMenu.grid(row=0,column=1,sticky=tk.W+tk.E)
		
		self._sensorPinLabel = ttk.Label(self._sensorSelectFrame,
										 text="Select Pin: ",
										 anchor=tk.E)
		self._sensorPinLabel.grid(row=1,column=0,sticky=tk.E+tk.W)
		self._sensorPinVar = tk.StringVar()
		self._sensorPinVar.set(settings.getCfg(self.cfgTitle,"rh_sensor_pin"))
		self._sensorPinInput = ttk.Entry(self._sensorSelectFrame,
										 textvariable=self._sensorPinVar,
										 justify=tk.CENTER)
		self._sensorPinInput.grid(row=1,column=1,sticky=tk.W+tk.E)
		
		self._sensorPeriodLabel = ttk.Label(self._sensorSelectFrame,
											text="Select Period: ",
											anchor=tk.E)
		self._sensorPeriodLabel.grid(row=2,column=0,sticky=tk.E+tk.W)
		self._sensorPeriodVar = tk.StringVar()
		self._sensorPeriodVar.set(settings.getCfg(self.cfgTitle,"rh_sensor_period"))
		self._sensorPeriodInput = ttk.Entry(self._sensorSelectFrame,
											textvariable=self._sensorPeriodVar,
											justify=tk.CENTER)
		self._sensorPeriodInput.grid(row=2,column=1,sticky=tk.W+tk.E)
		
		self._sensorLoadButton = ttk.Button(self._sensorSelectFrame,
											text="Load Sensor",
											command=self._loadSensor)
		self._sensorLoadButton.grid(row=3,column=0,columnspan=2)
		
		# Relative and humidity sensor outputs
		self._sensorOutputFrame = ttk.LabelFrame(self,text=self.fullTitle)
		self._sensorOutputFrame.pack(padx=5,pady=5,fill=tk.BOTH)
		tk.Grid.columnconfigure(self._sensorOutputFrame,0,weight=1)
		tk.Grid.columnconfigure(self._sensorOutputFrame,1,weight=1)
		
		self._timerStartLabel = ttk.Label(self._sensorOutputFrame,text="Started Recording: ",
										  anchor=tk.E)
		self._timerStartLabel.grid(row=0,column=0,padx=1,pady=1,sticky=tk.E+tk.W)
		self._timerStartOutputVar = tk.StringVar()
		self._timerStartOutputVar.set(time.strftime('%Y-%m-%d %H:%M:%S',
									  time.localtime(time.time())))
		self._timerStartOutput = ttk.Label(self._sensorOutputFrame,
										   textvariable=self._timerStartOutputVar,
										   justify=tk.CENTER)
		self._timerStartOutput.grid(row=0,column=1,padx=1,pady=1,sticky=tk.W+tk.E)
		
		self._timerLabel = ttk.Label(self._sensorOutputFrame,text="Last Recording: ",
									 anchor=tk.E)
		self._timerLabel.grid(row=1,column=0,padx=1,pady=1,sticky=tk.E+tk.W)
		self._timerOutputVar = tk.StringVar()
		self._timerOutputVar.set(time.strftime('%Y-%m-%d %H:%M:%S',
											   time.localtime(time.time())))
		self._timerOutput = ttk.Label(self._sensorOutputFrame,
									  textvariable=self._timerOutputVar,
									  justify=tk.CENTER)
		self._timerOutput.grid(row=1,column=1,padx=1,pady=1,sticky=tk.W+tk.E)
		
		self._rhLabel = ttk.Label(self._sensorOutputFrame,
								  text="Relative Humidity: ",
								  anchor=tk.E)
		self._rhLabel.grid(row=2,column=0,padx=1,pady=1,sticky=tk.E+tk.W)
		self._rhOutputVar = tk.StringVar()
		self._rhOutputVar.set("Nothing Received")
		self._rhOutput = ttk.Label(self._sensorOutputFrame,
								   textvariable=self._rhOutputVar,
								   justify=tk.CENTER)
		self._rhOutput.grid(row=2,column=1,padx=1,pady=1,sticky=tk.W+tk.E)
		
		self._tempLabel = ttk.Label(self._sensorOutputFrame,
									text="Temperature: ",
									anchor=tk.E)
		self._tempLabel.grid(row=3,column=0,padx=1,pady=1,sticky=tk.E+tk.W)
		self._tempOutputVar = tk.StringVar()
		self._tempOutputVar.set("Nothing Received")
		self._tempOutput = ttk.Label(self._sensorOutputFrame,
									 textvariable=self._tempOutputVar,
									 justify=tk.CENTER)
		self._tempOutput.grid(row=3,column=1,padx=1,pady=1,sticky=tk.W+tk.E)
		
		self._reset = tk.Button(self._sensorOutputFrame,
								text="CLEAR DATA",
								fg='red',
								command=self.reset_adapter)
		self._reset.grid(row=4,column=0,columnspan=1)
		
		self._saveData = ttk.Button(self._sensorOutputFrame,
									text="SAVE",
									command=self.save_data)
		self._saveData.grid(row=4,column=1,columnspan=1)
		if self.sensor_adapter:
			self._saveData.config(state=tk.ACTIVE)
		else:
			self._saveData.config(state=tk.DISABLED)
		
		# Humidifier Controls
		self._humidifier_dc = 0
		self._humidifierFrame = ttk.LabelFrame(self,
											   text="Humidifier Controller")
		self._humidifierFrame.pack(padx=5,pady=5,fill=tk.X)
		tk.Grid.columnconfigure(self._humidifierFrame,0,weight=1)
		tk.Grid.columnconfigure(self._humidifierFrame,1,weight=1)
		
		self._humidifierPinLabel = ttk.Label(self._humidifierFrame,
											 text="Pin: ")
		self._humidifierPinLabel.grid(row=0,column=0,columnspan=1,pady=5,sticky=tk.E)
		
		self._humidifierPinVar = tk.StringVar()
		self._humidifierPinVar.set(settings.getCfg(self.cfgTitle,"rh_humidifier_pin"))
		self._humidifierPinInput = ttk.Entry(self._humidifierFrame,
											 textvariable=self._humidifierPinVar,
											 justify=tk.CENTER)
		self._humidifierPinInput.grid(row=0,column=1,columnspan=1,pady=5)
		
		self._humidifierDutyLabel = ttk.Label(self._humidifierFrame,
											  text="Duty Cycle (%): ")
		self._humidifierDutyLabel.grid(row=1,column=0,columnspan=1,pady=5,sticky=tk.E)
		
		self._humidifierDutyCycle = tk.StringVar()
		self._humidifierDutyCycle.set(settings.getCfg(self.cfgTitle,"rh_humidifier_dc"))
		self._humidifierDutyInput = ttk.Entry(self._humidifierFrame,
											  textvariable=self._humidifierDutyCycle,
											  justify=tk.CENTER)
		self._humidifierDutyInput.grid(row=1,column=1,columnspan=1,pady=5)
		
		self._reset = tk.Button(self._humidifierFrame,
								text="Set",
								command=self._set_dc)
		self._reset.grid(row=2,column=0,columnspan=2)
		
		self._loadSensor()
		self._set_dc(True)
		self._print_sensor_data()
			
	def _print_sensor_data(self):
		if not self.sensor_adapter:
			self._timerOutputVar.set(time.strftime('%Y-%m-%d %H:%M:%S',
												   time.localtime(time.time())))
			self._sensorOutputFrame.after(int(float(settings.getCfg(self.cfgTitle,'rh_sensor_period'))*500),
										  self._print_sensor_data)
			return

		data = self.sensor_adapter.get_last_reading()
		if None in data.values():
			self._sensorOutputFrame.after(int(float(settings.getCfg(self.cfgTitle,'rh_sensor_period'))*500),
										  self._print_sensor_data)
			return
		
		timeval = data['Time']
		tempval = data['Temperature']
		humval = data['Relative Humidity']
		time_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeval))
		time_start_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.sensor_adapter.start_time()))
		temperature = '%.1f'%(tempval)
		humidity = '%.1f'%(humval)
		self._timerOutputVar.set(time_)
		self._tempOutputVar.set(temperature + " *C")
		self._rhOutputVar.set(humidity + " %")
		self._timerStartOutputVar.set(time_start_)
		
		self._sensorOutputFrame.after(int(float(settings.getCfg(self.cfgTitle,'rh_sensor_period'))*500),
									  self._print_sensor_data)
									  
	def save_data(self):
		if self.sensor_adapter:
			data = self.sensor_adapter.get_all_readings()
		else:
			return
		try:
			filename = asksaveasfilename()
			if not filename.endswith('csv'):
				filename += '.csv'
			data_file = open(filename, "wb")
			writer = csv.writer(data_file)
			writer.writerow(['Time', 'Temperature', 'Relative Humidity'])
			writer.writerow(['Start Time: ',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.sensor_adapter.start_time()))])
			for i in range(0,len(data['Time'])):
				writer.writerow([data['Time'][i],data['Temperature'][i],data['Relative Humidity'][i]])
			print('Saved')
		except TypeError:
			print('An error occured while saving data to csv file.')
									
	def _loadSensor(self,sensor=None):
		className = self._sensorSelectVar.get()
		if className in self._sensors.keys():
			if className=="None":
				self.set_sensor_config()
				self.sensor_adapter=None
				return
			try:
				mod = import_module(self._sensors[className])
				cl = getattr(mod,className)
				self.set_sensor_config(mod=self._sensors[className],
									   clazz=className,
									   period=self._sensorPeriodVar.get(),
									   pin=self._sensorPinVar.get())
				self.sensor_adapter = cl(pin=int(settings.getCfg(self.cfgTitle,'rh_sensor_pin')),
										 period=int(settings.getCfg(self.cfgTitle,'rh_sensor_period')))
				self.sensor_adapter.setTk(self)
				self.sensor_adapter.start_continuous_read()

			except ImportError as err:
				self.sensor_adapter=None
				self.set_sensor_config()
				self._sensorSelectVar.set("None")
				tkMessageBox.showerror(title=className,message=err)
		if self.sensor_adapter:
			self._saveData.config(state=tk.ACTIVE,
								  command=self.save_data)
		else:
			self._saveData.config(state=tk.DISABLED)

	def set_sensor_config(self,mod="None",clazz="None",period=2,pin=4):
		settings.setCfg(self.cfgTitle,"rh_sensor_class",clazz)
		settings.setCfg(self.cfgTitle,"rh_sensor_module",mod)
		settings.setCfg(self.cfgTitle,"rh_sensor_period",self._sensorPeriodVar.get())
		settings.setCfg(self.cfgTitle,"rh_sensor_pin",self._sensorPinVar.get())
		settings.saveCfg()
		
	def set_humidifier_config(self):
		settings.setCfg(self.cfgTitle,"rh_humidifier_pin",self._humidifierPinVar.get())
		settings.setCfg(self.cfgTitle,"rh_humidifier_dc",self._humidifierDutyCycle.get())
		settings.saveCfg()
		
	def _set_dc(self,hard_set=False):
		self._humidifier_dc = 100-int(self._humidifierDutyCycle.get())
		if self._humidifier_dc<0:
			self._humidifier_dc = 0
			self._humidifierDutyCycle.set('100')
		if self._humidifier_dc>100:
			self._humidifier_dc = 100
			self._humidifierDutyCycle.set('0')
		
		if hard_set or (self._humidifierPinVar.get() != settings.getCfg(self.cfgTitle,'rh_humidifier_pin')):
			GPIO.cleanup()
			GPIO.setup(int(self._humidifierPinVar.get()),GPIO.OUT)
			self.p = GPIO.PWM(int(self._humidifierPinVar.get()),0.5)
			self.p.start(100)
		else:
			self.p.ChangeDutyCycle(self._humidifier_dc)
			
		self.set_humidifier_config()
		
	def reset_adapter(self):
		if self.sensor_adapter:
			self.sensor_adapter.clear_readings()
		
if __name__ == "__main__":
	root = tk.Tk()
	panel = RHPanel(root)
	panel.pack()
	root.mainloop()
