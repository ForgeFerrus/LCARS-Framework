import importlib, time
m = importlib.import_module('lcars.core.board_computer')
print('MODULE', m)
c = m.get_computer()
print('GOT', type(c))
try:
    c.start()
    print('STARTED')
    time.sleep(0.5)
    c.shutdown()
    print('SHUTDOWN')
except Exception as e:
    import traceback
    traceback.print_exc()
    raise
