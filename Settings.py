import os
import sys
import ConfigParser

cfg = ConfigParser.ConfigParser()
path = sys.modules[__name__].__file__
path = path.replace(__file__,'settings.ini')

cfgDefaults = {}
cfgDefaults['RHTEMP'] = {'rh_sensor_module': 'None',
                         'rh_sensor_class': 'None',
                         'rh_sensor_pin': '4',
                         'rh_sensor_period': '2',
                         'rh_humidifier_dc': '0',
                         'rh_humidifier_pin': '20'}
                         
cfgDefaults['DEFAULT'] = {}
for key, options in cfgDefaults.items():
    for optKey, value in options.items():
        cfgDefaults['DEFAULT'][optKey] = value

def openCfg():
    global cfg
    
    if os.path.isfile(path):
        cfg.read(path)
        checkCfg()
    else:
        createCfg()

def createCfg():
    global cfg
    
    cfg = ConfigParser.ConfigParser(cfgDefaults['DEFAULT'])
    
    for section, options in cfgDefaults.items():
        if section=='DEFAULT': continue
        
        cfg.add_section(section)
        for option, value in options.items():
            cfg.set(section,option,value)
    saveCfg()
    
def setCfg(section,option,value):
    global cfg
    
    if not cfg.has_section(section):
        return False
    
    cfg.set(section,option,value)
    
    return True
    
def getCfg(section,option):
    global cfg
    
    if not cfg.has_section(section):
        return False
    
    return cfg.get(section,option,True)
    
def checkCfg():
    for section, options in cfgDefaults.items():
        if section=='DEFAULT': continue
        if not cfg.has_section(section):
            cfg.add_section(section)
            
        for option, value in options.items():
            if not cfg.has_option(section,option):
                cfg.set(section,option,cfgDefaults['DEFAULT'][option])
    
def saveCfg():
    with open(path,'wb') as cfgFile:
        cfg.write(cfgFile)
