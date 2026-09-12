"""Quick kernel boot test."""
import sys, io, logging

sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
logging.basicConfig(level=logging.ERROR)

from lcars.core.kernel import Kernel
Kernel.Reset()
from lcars.core.bootstrap import Start

K = Start(Gui=False)
print("State:", K.State)
print("Services:", len(K.Services.All()))
for name in K.Services.All():
    print(f"  {name}")
K.Shutdown()
print("Final:", K.State)
Kernel.Reset()
print("BOOT TEST PASSED")
