# Екран блокування (Lock Screen)
# Призначення: Відображається під час блокування системи. Дозволяє повернутись на робочий стіл після авторизації.
# Структура: Простий LCARS інтерфейс з кнопкою ACCESS.
import sys
from pathlib import Path
ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))
from lcars.base.default import FontSetup, Palette
from lcars.core.kernel import CreateApplication
from lcars.core.signal import Transmission
from lcars.base.type import LCARS
from lcars.base.component import LCARSBar, LCARSButton, LCARSLabel
from lcars.base.interface import Screen

class LCARSLock(Screen):

    def BuildScreen(self):
        pass

    def __init__(self, parent=None):
        super().__init__(Parent=parent)
        # Сигнали для переходу на робочий стіл
        self.access_granted = Transmission()
        self.desktop_requested = Transmission()
        
        self.alert_mode = False
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Build()

    def Build(self):
        VLayout = LCARS.VBox
        HLayout = LCARS.HBox
        Protocol = LCARS.Protocol

        self.Layout = VLayout(self.widget)
        self.Layout.setContentsMargins(24, 20, 24, 20)
        self.Layout.setSpacing(10)

        # ВЕРХНЯ ПАНЕЛЬ (Header)
        Top = HLayout()
        Top.setSpacing(8)
        self.TopCap = LCARSBar(Parent=self.widget, Color=Palette.Buttons[0], Width=190, Height=44)
        self.TopRail = LCARSBar(Parent=self.widget, Color=Palette.Buttons[5], Height=44)
        self.TopStatus = LCARSLabel(Text="LCARS SECURITY GRID", Parent=self.widget, Color=Palette.Panels[0], FontSize=22)
        Top.addWidget(self.TopCap.Widget)
        Top.addWidget(self.TopRail.Widget, 1)
        Top.addWidget(self.TopStatus.Widget)
        self.Layout.addLayout(Top)

        # ЦЕНТРАЛЬНА ЧАСТИНА (Body)
        Body = HLayout()
        Body.setSpacing(16)

        # Ліва колонка кнопок
        Left = VLayout()
        Left.setSpacing(8)
        self.AccessButton = LCARSButton(Text="ACCESS", Parent=self.widget, Type="pill", Color=Palette.Buttons[2], Width=220, Height=54)
        self.AccessButton.clicked.connect(self.AuthSuccess)
        
        self.AlertButton = LCARSButton(Text="ALERT", Parent=self.widget, Type="pill", Color=Palette.RedAlert[0], Width=220, Height=54)
        self.AlertButton.clicked.connect(self.ToggleAlert)
        
        Left.addWidget(self.AccessButton.Widget)
        Left.addWidget(self.AlertButton.Widget)
        Left.addStretch(1)
        Body.addLayout(Left)

        # Центральна колонка з інформацією
        Center = VLayout()
        Center.setSpacing(14)
        Center.setAlignment(Protocol.AlignmentFlag.AlignCenter if Protocol else 0)
        self.Title = LCARSLabel(Text="LCARS COMPUTER NETWORK", Parent=self.widget, Color=Palette.Panels[0], FontSize=42)
        self.Subtitle = LCARSLabel(Text="AUTHORIZED ACCESS ONLY", Parent=self.widget, Color=Palette.Panels[1], FontSize=20)
        self.Status = LCARSLabel(Text="SECURITY LOCK ACTIVE", Parent=self.widget, Color=Palette.Buttons[5], FontSize=18)
        Center.addWidget(self.Title.Widget)
        Center.addWidget(self.Subtitle.Widget)
        Center.addWidget(self.Status.Widget)
        Body.addLayout(Center, 1)

        # Права колонка кнопок
        Right = VLayout()
        Right.setSpacing(8)
        for LabelText, Color in [
            ("BIOS", Palette.Buttons[0]),
            ("KERNEL", Palette.Buttons[1]),
            ("REGISTRY", Palette.Buttons[2]),
            ("DATABASE", Palette.Buttons[3]),
            ("SECURITY", Palette.Buttons[4]),
        ]:
            Row = LCARSButton(Text=LabelText, Parent=self.widget, Type="soft", Color=Color, Width=190, Height=42)
            Right.addWidget(Row.Widget)
        Right.addStretch(1)
        Body.addLayout(Right)
        
        self.Layout.addLayout(Body, 1)

        # НИЖНЯ ПАНЕЛЬ (Footer)
        Bottom = HLayout()
        Bottom.setSpacing(8)
        
        # Індикатор/Кнопка блокування
        self.LockButton = LCARSButton(Text="LOCK", Parent=self.widget, Type="pill", Color=Palette.Panels[0], Width=110, Height=34)
        self.LockButton.clicked.connect(self.ExecuteLock)
        
        self.BottomRail = LCARSBar(Parent=self.widget, Color=Palette.Buttons[5], Height=18)
        Bottom.addWidget(self.LockButton.Widget)
        Bottom.addWidget(self.BottomRail.Widget, 1)
        self.Layout.addLayout(Bottom)

    # ДІЇ

    def ExecuteLock(self):
        self.Status.SetText("SECURITY LOCK ACTIVE")
        self.Status.SetColor(Palette.Buttons[5])
        self.AccessButton.SetText("ACCESS")
        self.AccessButton.SetColor(Palette.Buttons[2])

    def AuthSuccess(self):
        self.Status.SetText("ACCESS GRANTED")
        self.Status.SetColor(Palette.Panels[2])
        self.AccessButton.SetText("GRANTED")
        self.AccessButton.SetColor(Palette.Panels[2])
        LCARS.Timer.singleShot(400, self.LaunchDesktop)

    def LaunchDesktop(self):
        self.access_granted.Emit()
        self.desktop_requested.Emit()

    def ToggleAlert(self):
        self.alert_mode = not self.alert_mode
        if self.alert_mode:
            self.Status.SetText("RED ALERT ACTIVE")
            self.Status.SetColor(Palette.RedAlert[0])
            self.AlertButton.SetText("NORMAL")
        else:
            self.Status.SetText("SECURITY LOCK ACTIVE")
            self.Status.SetColor(Palette.Buttons[5])
            self.AlertButton.SetText("ALERT")

    def closeEvent(self, event):
        if event is not None:
            event.accept()

# ЗАПУСК ТЕСТУ
if __name__ == "__main__":
    app = CreateApplication(sys.argv)
    if app is not None:
        FontSetup()
        Display = LCARSLock()
        Display.show()
        sys.exit(app.exec())
    sys.exit(1)
