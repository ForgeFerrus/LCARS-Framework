import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from tools.weather_station import WeatherEngine
import time
eng = WeatherEngine()
print('Signal obj:', type(eng.CurrentWeatherSignal), repr(eng.CurrentWeatherSignal))
print('Has connect:', hasattr(eng.CurrentWeatherSignal, 'connect'))
print('Has emit:', hasattr(eng.CurrentWeatherSignal, 'emit'))

def cb(data):
    print('CB DATA:', data)

eng.CurrentWeatherSignal.connect(cb)
eng.IsLocationEstablished = True
eng.RefreshAtmosCurrentCondition()
for i in range(8):
    print('tick', i)
    time.sleep(1)
print('done')
