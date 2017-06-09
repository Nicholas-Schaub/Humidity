import abc
import threading
from pprint import pprint
import time

class RHSensor:
    __metaclass__ = abc.ABCMeta
    
    # Private properties for looping
    _tk = None      # tkinter object to insert into mainloop
    _continue_loop = False
    
    is_rh_sensor = False
    
    _data = {}
    _data_categories = [] # data_categories must be defined by subclass
    _data_units = []      # units for each data category
    
    _sensor = None
    _period = 5
    _pin = 4
    _min_period = 2       # minimum polling period
    
    _start_time = None
    
    _print_data = False   # set to true to print data in console
    
    # Unique property get and set functions
    @property
    def period(self):
        return self._period
    
    @period.setter
    def period(self,newPeriod):
        if newPeriod<self._min_period:
            self._period = self._min_period
        else:
            self._period = newPeriod
        
    @property
    def data_categories(self):
        if _data_categories == None:
            AttributeError('data_categories is undefined')
        else:
            return _data_categories
    
    @data_categories.setter 
    def data_categories(self,new_categories):
        new_categories = [cat.replace('time','Time') for cat in new_categories]
        
        if 'Time' not in new_categories:
            KeyError("''Time'' must be one of the categories")
        
        self._data = {'Time': []}
        self._data_categories = new_categories
        for category in new_categories:
            if category == 'Time':
                continue
            self._data[category] = []
    
    # Abstract methods
    @abc.abstractmethod
    def __init__(self,pin,period,sensor):
        """
        The __init__ method for RHSensor sublcasses should initialize a
        connection with a temperature/humidity sensor. 
        
        Inputs:
        pin - the Raspberry Pi GPIO pin that the sensor is connected to
        period - The time interval between attempts to read the sensor
        """
        
    @abc.abstractmethod
    def _read_sensor(self):
        """
        The read_sensor method should be implemented by each subclass of
        RHSensor, which directly reads data off of the sensor. This
        method should return a dictionary where the keys are
        _data_categories. One of the categories must be 'Time',
        which is the time in seconds since epoch when the reading was
        taken.
        """
        
    def read_sensor(self):
        result = self._read_sensor()
        if self._print_data:
            pprint(result)
            
        return result
    
    def setTk(self,tk):
        _tk = tk
    
    def start_continuous_read(self):
        """
        The start_continuous_read method should start polling the
        sensor at regular time intervals, where the time interval is
        designated by the period property. This method should create a
        thread to do continuous polling. Alternatively, if a tk instance
        is defined, the polling frequency can be added to the main_loop.
        """
        self._start_time = time.time()
        self._continue_loop = True
        if self._tk==None:
            self.thread = threading.Thread(target=self._read_loop,args=())
            self.thread.start()
        else:
            self._tk.after(self._period,self._read_loop)
            
    def _read_loop(self):
        """
        The _read_loop method should be run as 1) a while loop where
        _read_loop should be run on its own thread or 2) inside a
        tkinter mainloop.
        """
        if self._tk==None:
            while self._continue_loop:
                self._append_reading(self.read_sensor())
                time.sleep(self._period)
        else:
            if self._continue_loop:
                self._append_reading(self.read_sensor())
                self._tk.after(self._period*1000,self._read_loop)
                
    def _append_reading(self,data):
        for category in self._data_categories:
            self._data[category].append(data[category])
    
    def get_last_reading(self):
        """
        Get the values of the most recent sensor reading.
        """
        result = {}
        if len(self._data['Time'])==0:
            result = {'Time': None}
        else:
            for category in self._data_categories:
                result[category] = self._data[category][-1]
            
        return result
        
    def stop_continuous_read(self):
        self._continue_loop = False
        
    def is_continuous_read(self):
        return self._continue_loop
        
    def get_all_readings(self):
        return self._data
        
    def print_console(self,boolean):
        self._print_data = boolean
        
    def clear_readings(self):
        for category in self._data_categories:
            self._data[category] = []
        self._start_time = time.time()
        
    def start_time(self):
        return self._start_time
