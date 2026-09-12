import importlib
m = importlib.import_module('lcars.base.types')
print('MODULE_FILE:', getattr(m,'__file__',None))
print('HAS_Widget:', hasattr(m,'Widget'))
print('HAS_Label:', hasattr(m,'Label'))
print('ALL_KEYS:', [k for k in dir(m) if k in ('Widget','Label','VBoxLayout')])
