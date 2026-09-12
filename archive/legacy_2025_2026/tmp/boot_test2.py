"""Boot test script"""
import sys, io, logging
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, '.')
logging.basicConfig(level=logging.INFO)

from lcars.core.kernel import Kernel
Kernel.Reset()
from lcars.core.bootstrap import Start

K = Start(Gui=False)
print('KERNEL_STATE:', getattr(K, 'State', None))
services = K.Services.All()
print('SERVICES_COUNT:', len(services))
for name in services:
    print(' SERVICE:', name)

K.Shutdown()
Kernel.Reset()
print('BOOT_TEST_DONE')
