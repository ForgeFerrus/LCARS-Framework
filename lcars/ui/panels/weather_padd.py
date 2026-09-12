# LCARS Weather PADD - Окрема погода
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
sys.path.insert(0, r'c:\Users\Forge\MyProject\LCARS-Framework')

from lcars.base.interface import LCARSPadd
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, PillButton
from lcars.base.type import Layout, Directive
from lcars.base.default import RandomButtonColor
from lcars.modules.net import NetworkManager


class WeatherPADD(LCARSPadd):

    def __init__(self, Parent=None):
        super().__init__(Title="WEATHER", Color="#00CCFF", Parent=Parent)
        self.Network = NetworkManager()
        
        _ = self.Native
        self.Native.setStyleSheet("background-color: #000000;")
        self.Native.setFixedSize(300, 400)
        
        self.CreateComponents()
        
        self.Timer = Directive.Chronometer(self)
        self.Timer.timeout.connect(self.UpdateWeather)
        self.Timer.start(300000)
        
        self.UpdateWeather()

    def CreateComponents(self):
        Target = getattr(self, 'Viewport', self.Native)
        
        Root = Layout.VBox(Target)
        Root.setContentsMargins(16, 16, 16, 16)
        Root.setSpacing(12)
        
        # Header
        Header = Layout.HBox()
        Header.setSpacing(8)
        HLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_left", Thickness=32, Radius=32)
        HLElbow.setFixedSize(60, 60)
        Header.addWidget(HLElbow)
        HLPill = PillButton(Color=RandomButtonColor())
        HLPill.setFixedSize(8, 32)
        Header.addWidget(HLPill)
        Title = LCARSLabel("WEATHER", Color="#00CCFF", FontSize=18)
        Header.addWidget(Title)
        Header.addStretch()
        HRPill = PillButton(Color=RandomButtonColor())
        HRPill.setFixedSize(8, 32)
        Header.addWidget(HRPill)
        HRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_right", Thickness=32, Radius=32)
        HRElbow.setFixedSize(60, 60)
        Header.addWidget(HRElbow)
        Root.addLayout(Header)
        Root.addSpacing(16)
        
        # Temperature
        self.TempLbl = LCARSLabel("--°C", Color="#00CCFF", FontSize=48)
        self.TempLbl.setStyleSheet("padding: 20px;")
        Root.addWidget(self.TempLbl)
        
        self.DescLbl = LCARSLabel("Loading...", Color="#888888", FontSize=14)
        Root.addWidget(self.DescLbl)
        Root.addSpacing(16)
        
        # Details
        Details = Layout.VBox()
        Details.setSpacing(8)
        self.WindLbl = LCARSLabel("Wind: -- km/h", Color=RandomButtonColor(), FontSize=12)
        Details.addWidget(self.WindLbl)
        Root.addLayout(Details)
        Root.addStretch()
        
        # Refresh
        RefreshBtn = LCARSButton("REFRESH", Color=RandomButtonColor())
        RefreshBtn.setFixedHeight(40)
        RefreshBtn.Clicked = self.UpdateWeather
        Root.addWidget(RefreshBtn)
        Root.addSpacing(8)
        
        # Menu button
        MenuBtn = LCARSButton("MENU", Color="#FF9900")
        MenuBtn.setFixedHeight(36)
        MenuBtn.Clicked = self.OpenMenu
        Root.addWidget(MenuBtn)
        Root.addSpacing(8)
        
        # Footer
        Footer = Layout.HBox()
        Footer.setSpacing(8)
        BLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_left", Thickness=32, Radius=32)
        BLElbow.setFixedSize(60, 60)
        Footer.addWidget(BLElbow)
        FLPill = PillButton(Color=RandomButtonColor())
        FLPill.setFixedSize(8, 32)
        Footer.addWidget(FLPill)
        Footer.addStretch()
        FRPill = PillButton(Color=RandomButtonColor())
        FRPill.setFixedSize(8, 32)
        Footer.addWidget(FRPill)
        BRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_right", Thickness=32, Radius=32)
        BRElbow.setFixedSize(60, 60)
        Footer.addWidget(BRElbow)
        Root.addLayout(Footer)
        
        Target.setLayout(Root)

    def UpdateWeather(self):
        Url = "https://api.open-meteo.com/v1/forecast?latitude=50.45&longitude=30.52&current_weather=true"
        Success, Data = self.Network.RequestJson(Url, Timeout=5)
        if Success and isinstance(Data, dict):
            Current = Data.get("current_weather", {})
            Temp = Current.get("temperature", "--")
            Code = Current.get("weathercode", 0)
            Wind = Current.get("windspeed", "--")
            self.TempLbl.setText(f"{Temp}°C")
            self.DescLbl.setText(self.WeatherCodeToDesc(Code))
            self.WindLbl.setText(f"Wind: {Wind} km/h")
        else:
            self.TempLbl.setText("ERR")
            self.DescLbl.setText("Connection failed")

    def WeatherCodeToDesc(self, Code):
        Codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 51: "Light drizzle", 53: "Moderate drizzle", 61: "Slight rain",
            63: "Moderate rain", 71: "Slight snow", 95: "Thunderstorm"
        }
        return Codes.get(Code, "Unknown")


    def OpenMenu(self):
        # Відкрити головне меню
        from lcars.base.type import Chassis
        if not Chassis.Application.instance():
            return
        # Тут можна відкрити меню або повернутись на desktop
        print("[WEATHER] Menu button clicked")

if __name__ == "__main__":
    from lcars.base.default import FontSetup
    from lcars.base.type import Chassis
    
    FontSetup()
    App = Chassis.Application(sys.argv)
    PADD = WeatherPADD()
    PADD.Show()
    sys.exit(App.exec())
