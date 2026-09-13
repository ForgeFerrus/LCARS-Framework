# LCARS signal system test.
# Перевіряє Observer, Transmission і ODN без символів, які ламають Windows-консоль.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lcars.core.signal import ODN, Observer, Transmission


def test_signal_system():
    ObserverCalled = False

    def TestCallback(Data):
        nonlocal ObserverCalled
        ObserverCalled = True

    ObserverNode = Observer(str)
    ObserverNode.Attach(TestCallback)
    ObserverNode.Update("test data")

    assert ObserverCalled, "Observer Update failed"
    print("[OK] Observer")

    TransmissionCalled = False

    def TransmissionCallback(Message):
        nonlocal TransmissionCalled
        TransmissionCalled = True

    TransmissionNode = Transmission(str)
    TransmissionNode.Connect(TransmissionCallback, "test_channel")
    TransmissionNode.Emit("hello", Channel="test_channel")

    assert TransmissionCalled, "Transmission Emit failed"
    print("[OK] Transmission")

    ODNCalled = False

    def ODNCallback(Data):
        nonlocal ODNCalled
        ODNCalled = True

    ODN.Link("Updates.Data", ODNCallback)
    ODN.Send("Updates.Data", "ODN test data")

    assert ODNCalled, "ODN Send failed"
    print("[OK] ODN")

    ODN.Shutdown()
    assert len(ODN.Channels) == 0, "ODN Shutdown failed"
    print("[OK] Shutdown")

    print("ALL SIGNAL TESTS PASSED")
    return True


if __name__ == "__main__":
    test_signal_system()
