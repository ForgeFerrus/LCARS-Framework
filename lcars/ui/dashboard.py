from lcars.base.interface import PADD
from lcars.base.type import LCARS
from lcars.service.provider import getProvider
from core.signal import Transmission

class OnboardComputer(PADD):
    def __init__(self, ParentNode=None, **kwargs):
        # Ініціалізуємо провайдера
        self.provider = getProvider()
        if not self.provider.initialized:
            self.provider.initialize()
            
        # Отримуємо імена реальних бекендів для автоматичної генерації кнопок меню
        self.ModelNames = []
        for backend in self.provider.backends:
            if backend.name != "fallback":
                self.ModelNames.append(backend.name.upper())
                
        if not self.ModelNames:
            self.ModelNames = ["OFFLINE"]

        # Передаємо Value, щоб PADD автоматично згенерував кнопки меню з рандом-алгоритмом кольорів
        super().__init__(
            Title="ONBOARD AI DASHBOARD",
            Value=self.ModelNames,
            ParentNode=ParentNode,
            **kwargs
        )
        
        self.BuildDashboard()

    def BuildDashboard(self):
        # Підключаємо автоматично згенеровані кнопки меню до логіки перемикання моделей
        for index, name in enumerate(self.ModelNames):
            btn = self.Items.get(f"Button{index}")
            if btn:
                # Використовуємо лямбду із замиканням
                btn.clicked.connect(lambda ch, n=name: self.SwitchModel(n))

        # Отримуємо рідний контейнер контенту PADD'а
        ContentLayout = self.Items["Content"].Layout
        ContentWidget = self.Items["Content"].widget

        # ── ОСНОВНИЙ ЕКРАН ВИВОДУ ──
        self.OutputArea = LCARS.Terminal(ContentWidget)
        self.OutputArea.setReadOnly(True)
        ContentLayout.addWidget(self.OutputArea, 1)

        # ── ПОЛЕ ВВОДУ ЗАПИТУ ──
        # Контейнер для вводу, щоб додати кнопку виконання
        InputPanel = LCARS.Panel(Parent=ContentWidget)
        InputPanel.setFixedHeight(50)
        InputPanel.setStyleSheet("background-color: transparent;")
        InputLayout = LCARS.Horizontal(InputPanel)
        InputLayout.setContentsMargins(0, 0, 0, 0)
        InputLayout.setSpacing(10)

        self.InputField = LCARS.TextEdit(InputPanel)
        self.InputField.setPlaceholderText("Transmit query to AI...")
        
        # Підміна обробника Enter без QObject/installEventFilter
        self._OriginalKeyPress = self.InputField.keyPressEvent
        self.InputField.keyPressEvent = self.OnInputKeyPress
        
        InputLayout.addWidget(self.InputField, 1)

        ContentLayout.addWidget(InputPanel)

        # Встановлюємо перший активний бекенд
        if self.ModelNames and self.ModelNames[0] != "OFFLINE":
            self.SwitchModel(self.ModelNames[0])
        else:
            self.PrintResponse("◤ ERROR: NO AI BACKENDS AVAILABLE.")

    def OnInputKeyPress(self, event):
        if event.key() in (LCARS.Protocol.Key.Key_Return, LCARS.Protocol.Key.Key_Enter):
            self.SendQuery()
            return
        self._OriginalKeyPress(event)

    def SwitchModel(self, model_name: str):
        self.PrintResponse(f"> SYSTEM RE-ROUTED TO: {model_name} CORE.")
        self.provider.manualOverride = True
        
        # Шукаємо відповідний бекенд
        for backend in self.provider.backends:
            if backend.name.upper() == model_name:
                self.provider.activeBackend = backend
                break
                
        # Змінюємо заголовок PADD'а
        if "Title" in self.Items:
            self.Items["Title"].SetText(f"ONBOARD AI :: {model_name}")

    def SendQuery(self):
        query = self.InputField.toPlainText().strip()
        if not query:
            return
            
        self.PrintResponse(f"USR> {query}")
        self.InputField.clear()
        
        active_name = self.provider.activeBackend.name.upper() if self.provider.activeBackend else "OFFLINE"
        self.PrintResponse(f"{active_name}> Processing...")
        
        # Асинхронний запит
        Transmission(lambda: self.provider.ask(query)).send(self.HandleResponse)

    def HandleResponse(self, response):
        if not response:
            response = "◤ ERROR: NO DATA RECEIVED."
            
        active_name = self.provider.activeBackend.name.upper() if self.provider.activeBackend else "OFFLINE"
        self.PrintResponse(f"{active_name}> {response}")

    def PrintResponse(self, text):
        self.OutputArea.insertPlainText(text + "\n")
        scrollbar = self.OutputArea.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
