# ◤ TITANIUM LCARS :: CONTROL NETWORK CONDUIT 🖖
# =============================================================================
# ФАЙЛ: programs/Control/daemon.py
# ПРИЗНАЧЕННЯ: UI-фасад канонічного NetworkSubsystem. Власного сервера тут
#              немає: gateway і firewall належать виключно lcars.service.network.
# =============================================================================

from lcars.base.type import LCARS


class GatewayDaemon:
    SingletonInstance = None

    def __init__(self):
        self.LogCallbacks = []
        self.Host = "127.0.0.1"
        self.Port = 3688
        self.SyncNetworkStatus()

    @classmethod
    def GetInstance(cls):
        if cls.SingletonInstance is None:
            cls.SingletonInstance = GatewayDaemon()
        return cls.SingletonInstance

    def GetNetworkService(self):
        NetworkModule = LCARS.Import("lcars.service.network")
        return NetworkModule.NetworkSubsystem.GetInstance() if NetworkModule else None

    def SyncNetworkStatus(self):
        Service = self.GetNetworkService()
        if Service:
            self.Host = Service.GatewayHost
            self.Port = Service.GatewayPort

    def RegisterLogCallback(self, Callback):
        if callable(Callback) and Callback not in self.LogCallbacks:
            self.LogCallbacks.append(Callback)

    def UnregisterLogCallback(self, Callback):
        if Callback in self.LogCallbacks:
            self.LogCallbacks.remove(Callback)

    def DispatchLog(self, MessageText):
        CleanText = str(MessageText).strip()
        if not CleanText:
            return
        DateTimeModule = LCARS.Import("datetime").datetime
        Record = "[" + DateTimeModule.now().strftime("%H:%M:%S") + "] " + CleanText
        for Callback in self.LogCallbacks:
            Callback(Record)

    def IsActive(self):
        Service = self.GetNetworkService()
        return bool(Service and Service.IsGatewayActive())

    def GetPid(self):
        return None

    def GetUptimeSeconds(self):
        Service = self.GetNetworkService()
        if not Service or not Service.GatewayStartedAt:
            return 0
        TimeModule = LCARS.Import("time")
        return int(TimeModule.time() - Service.GatewayStartedAt)

    def GetFormattedUptime(self):
        if not self.IsActive():
            return "—"
        Hours, Rest = divmod(self.GetUptimeSeconds(), 3600)
        Minutes, Seconds = divmod(Rest, 60)
        return str(Hours).zfill(2) + ":" + str(Minutes).zfill(2) + ":" + str(Seconds).zfill(2)

    def GetFirewallStatus(self):
        Service = self.GetNetworkService()
        return Service.GetFirewallStatus() if Service else {}

    def StartDaemon(self):
        Service = self.GetNetworkService()
        if not Service:
            self.DispatchLog(">> [ERROR]: NetworkSubsystem is unavailable.")
            return False
        if Service.StartGateway():
            self.SyncNetworkStatus()
            self.DispatchLog("✓ Network gateway online // " + self.Host + ":" + str(self.Port) + " // firewall: loopback-only")
            return True
        self.DispatchLog(">> [ERROR]: Gateway refused by inbound firewall policy.")
        return False

    def StopDaemon(self):
        Service = self.GetNetworkService()
        if not Service:
            return False
        Service.StopGateway()
        self.DispatchLog("✓ Network gateway offline.")
        return True

    def RestartDaemon(self):
        self.StopDaemon()
        return self.StartDaemon()
