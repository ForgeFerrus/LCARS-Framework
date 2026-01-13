import time
import sys
print('quick_echo start')
print('args:', sys.argv[1:])
sys.stdout.flush()
# short sleep to keep process alive briefly
time.sleep(0.5)
print('quick_echo done')
