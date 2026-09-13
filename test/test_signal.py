# LCARS FRAMEWORK v0.1.0-alpha
# ТЕСТИ СИСТЕМИ СИГНАЛІЗАЦІЇ
# ─────────────────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lcars.base.signal import Observer, Transmission, ODN

def test_signal_system():
    # 1. Тест Observer
    observer_called = False
    def test_callback(data):
        nonlocal observer_called
        observer_called = True
    
    obs = Observer(str)
    obs.Attach(test_callback)
    obs.Update("test data")
    
    assert observer_called, "Observer Update failed"
    print("✅ Observer: PASSED")
    
    # 2. Тест Transmission
    trans_called = False
    def trans_callback(msg):
        nonlocal trans_called
        trans_called = True
    
    trans = Transmission(str)
    trans.Connect(trans_callback, "test_channel")
    trans.Emit("hello", Channel="test_channel")
    
    assert trans_called, "Transmission Emit failed"
    print("✅ Transmission: PASSED")
    
    # 3. Тест ODN
    odn_called = False
    def odn_callback(data):
        nonlocal odn_called
        odn_called = True

    ODN.Link("Updates.Data", odn_callback)
    ODN.Send("Updates.Data", "ODN test data")

    assert odn_called, "ODN Send failed"
    print("✅ ODN: PASSED")
    
    # 4. Тест Shutdown
    ODN.Shutdown()
    assert len(ODN.Channels) == 0, "ODN Shutdown failed"
    print("✅ Shutdown: PASSED")
    
    print("◤ ALL SIGNAL TESTS: PASSED")
    return True

if __name__ == "__main__":
    test_signal_system()
