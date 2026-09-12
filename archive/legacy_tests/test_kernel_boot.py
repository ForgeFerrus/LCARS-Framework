# ◤ LCARS KERNEL BOOT TEST
# Перевіряє повний цикл: Start → Boot → Services → Shutdown.
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lcars.core.kernel import Kernel, SystemState, EventBus, Event, Store
from lcars.core.service import Service
from lcars.core.process import Application
from lcars.core.bootstrap import Start, GetKernel, ConfigSubsystem, AlertSubsystem


class TestEventBus(unittest.TestCase):

    def setUp(self):
        self.Bus = EventBus()

    def test_emit_and_listen(self):
        Received = []
        self.Bus.On("test.ping", lambda E: Received.append(E))
        self.Bus.Emit("test.ping", "unit")
        self.assertEqual(len(Received), 1)
        self.assertEqual(Received[0].Type, "test.ping")

    def test_wildcard(self):
        All = []
        self.Bus.On("*", lambda E: All.append(E))
        self.Bus.Emit("a", "x")
        self.Bus.Emit("b", "y")
        self.assertEqual(len(All), 2)

    def test_off(self):
        Count = []
        Cb = lambda E: Count.append(1)
        self.Bus.On("x", Cb)
        self.Bus.Emit("x", "s")
        self.Bus.Off("x", Cb)
        self.Bus.Emit("x", "s")
        self.assertEqual(len(Count), 1)

    def test_history(self):
        self.Bus.Emit("h.1", "s")
        self.Bus.Emit("h.2", "s")
        H = self.Bus.GetHistory()
        self.assertEqual(len(H), 2)
        Filtered = self.Bus.GetHistory("h.1")
        self.assertEqual(len(Filtered), 1)


class TestStore(unittest.TestCase):

    def setUp(self):
        self.Bus = EventBus()
        self.Store = Store(self.Bus)

    def test_set_get(self):
        self.Store.Set("key", 42)
        self.assertEqual(self.Store.Get("key"), 42)

    def test_default(self):
        self.assertIsNone(self.Store.Get("missing"))
        self.assertEqual(self.Store.Get("missing", 7), 7)

    def test_event_on_change(self):
        Events = []
        self.Bus.On("store.changed", lambda E: Events.append(E))
        self.Store.Set("x", 1)
        self.assertEqual(len(Events), 1)
        self.assertEqual(Events[0].Data["Key"], "x")

    def test_delete(self):
        self.Store.Set("d", 1)
        self.Store.Delete("d")
        self.assertFalse(self.Store.Has("d"))

    def test_snapshot(self):
        self.Store.Set("a", 1)
        self.Store.Set("b", 2)
        Snap = self.Store.Snapshot()
        self.assertEqual(Snap, {"a": 1, "b": 2})


class TestSubsystem(unittest.TestCase):

    def test_custom_service(self):
        class PingSubsystem(Service):
            Name = "ping"
            Started = False
            def OnStart(self):
                PingSubsystem.Started = True
            def OnStop(self):
                PingSubsystem.Started = False

        Kernel.Reset()
        K = Kernel()
        K.Register(PingSubsystem())
        K.Boot()
        self.assertTrue(PingSubsystem.Started)
        self.assertEqual(K.Phase, SystemState.RUNNING)

        K.Shutdown()
        self.assertFalse(PingSubsystem.Started)
        self.assertEqual(K.Phase, SystemState.OFF)
        Kernel.Reset()

    def test_dependencies(self):
        Order = []

        class A(Service):
            Name = "a"
            def OnStart(self):
                Order.append("a")

        class B(Service):
            Name = "b"
            Dependencies = ["a"]
            def OnStart(self):
                Order.append("b")

        Kernel.Reset()
        K = Kernel()
        K.Register(B())
        K.Register(A())
        K.Boot()
        self.assertEqual(Order, ["a", "b"])
        Kernel.Reset()


class TestApplication(unittest.TestCase):

    def test_launch_and_kill(self):
        Kernel.Reset()
        K = Kernel()
        K.Boot()

        class TestApp(Application):
            AppId = "test.app"
            Title = "Test"
            Launched = False
            Closed = False
            def OnLaunch(self, KRef):
                TestApp.Launched = True
                self.Kernel = KRef
            def OnClose(self):
                TestApp.Closed = True

        Pid = K.Launch(TestApp())
        self.assertTrue(TestApp.Launched)
        self.assertEqual(K.Processes.Count(), 1)

        K.Kill(Pid)
        self.assertTrue(TestApp.Closed)
        self.assertEqual(K.Processes.Count(), 0)
        Kernel.Reset()


class TestBootstrap(unittest.TestCase):

    def test_full_start(self):
        Kernel.Reset()
        K = Start(Gui=False)

        self.assertIn(K.Phase, (SystemState.RUNNING, SystemState.DEGRADED))

        # ConfigSubsystem loaded
        Cfg = K.Services.Get("config")
        self.assertIsNotNone(Cfg)
        self.assertIsInstance(Cfg, ConfigSubsystem)

        # AlertSubsystem active
        Alert = K.Services.Get("alert")
        self.assertIsNotNone(Alert)
        self.assertEqual(Alert.GetLevel(), "GREEN")

        # ExtensionSubsystem registered
        Plugins = K.Services.Get("plugins")
        self.assertIsNotNone(Plugins)

        # Config loaded from disk
        MainCfg = Cfg.Get("config")
        # config/config.json should exist
        self.assertIsNotNone(MainCfg)

        # Alert can change
        Alert.SetLevel("RED")
        self.assertEqual(Alert.GetLevel(), "RED")
        self.assertEqual(K.State.Get("alert.level"), "RED")

        # GetKernel returns same instance
        self.assertIs(GetKernel(), K)

        # Status report works
        Status = K.Status()
        self.assertIn("Phase", Status)
        self.assertIn("config", Status["Services"]["Registered"])

        K.Shutdown()
        self.assertEqual(K.Phase, SystemState.OFF)
        Kernel.Reset()


if __name__ == "__main__":
    unittest.main()
