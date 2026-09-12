# LCARS NETWORK INTERFACE
# Об'єднаний модуль комунікатора та браузера для доступу до мережі
# Відповідає строгим правилам архітектури LCARS

from lcars.base.type import LCARS, Matrix
from lcars.base.component import LCARSButton, LCARSIndicator
from lcars.base.interface import Segment, Header, Footer

class NetworkInterface(Matrix):
    # Головна матриця мережевого доступу
    # Об'єднує функції перегляду мережі та зв'язку
    
    def __init__(self, Parent=None):
        super().__init__(Parent=Parent)
        self.Mode = "inner"
        self.Bookmarks = [
            ("STARFLEET COMMAND", "https://www.startrek.com"),
            ("MEMORY ALPHA", "https://memory-alpha.fandom.com"),
            ("FEDERATION DB", "https://github.com")
        ]
        self.BuildUi()

    def BuildUi(self):
        # Побудова графічного інтерфейсу матриці
        Layout = getattr(self.widget, "layout")()
        
        self.HeaderBlock = Header(Title="NETWORK UPLINK", Parent=self.widget)
        self.Add(Layout, self.HeaderBlock)

        self.MainSegment = Segment(Parent=self.widget)
        self.MainLayout = self.MainSegment.Horizontal(0, 0, 0, 0, 10)
        
        self.BuildSidebar()
        self.BuildWorkspace()
        
        self.Add(Layout, self.MainSegment, 1)

        self.FooterBlock = Footer(Title="STANDBY", Parent=self.widget)
        self.Add(Layout, self.FooterBlock)

    def BuildSidebar(self):
        # Бічна панель із закладками
        self.SideSegment = Segment(Parent=self.MainSegment.widget)
        self.SideSegment.widget.setFixedWidth(250)
        self.SideLayout = self.SideSegment.Vertical(0, 0, 0, 0, 6)
        
        TitleWeb = LCARSIndicator("BOOKMARKS", Type="title", Color="#FF9900", Parent=self.SideSegment.widget)
        self.Add(self.SideLayout, TitleWeb)
        
        for Label, Url in self.Bookmarks:
            BtnWeb = LCARSButton(Label, "#FF9900", shape="rect", Parent=self.SideSegment.widget)
            BtnWeb.clicked.Connect(lambda *args, TargetUrl=Url: self.NavigateUrl(TargetUrl))
            self.Add(self.SideLayout, BtnWeb)
            
        self.AddStretch(self.SideLayout)
        self.Add(self.MainLayout, self.SideSegment)

    def BuildWorkspace(self):
        # Робоча область для браузера
        self.WorkSegment = Segment(Parent=self.MainSegment.widget)
        self.WorkLayout = self.WorkSegment.Vertical(0, 0, 0, 0, 8)
        
        self.InputArea = Segment(Parent=self.WorkSegment.widget)
        self.InputLayout = self.InputArea.Horizontal(0, 0, 0, 0, 6)
        
        InputClass = LCARS.Input
        self.DataInput = InputClass()
        self.DataInput.setPlaceholderText("ENTER URL...")
        self.DataInput.setStyleSheet("background: #000; color: #FFF; border: 1px solid #FF9900; font-size: 18px; padding: 4px;")
        self.Add(self.InputLayout, self.DataInput, 1)
        
        BtnAction = LCARSButton("EXECUTE", "#FF9900", shape="pill", Parent=self.InputArea.widget)
        BtnAction.clicked.Connect(self.ProcessInput)
        self.Add(self.InputLayout, BtnAction)
        
        self.Add(self.WorkLayout, self.InputArea)
        
        WebViewClass = LCARS.Web.View
        self.WebView = WebViewClass()
        if hasattr(self.WebView, "page"):
            self.WebView.page().setBackgroundColor(LCARS.Color("black"))
            
        self.Add(self.WorkLayout, self.WebView, 1)
        self.Add(self.MainLayout, self.WorkSegment, 1)

    def NavigateUrl(self, Url):
        # Завантаження сторінки у браузер
        if not Url.startswith("http"):
            Url = "https://" + Url
        UrlClass = LCARS.Url
        self.WebView.setUrl(UrlClass(Url))
        self.SetStatus("LOADING: " + Url)

    def ProcessInput(self):
        # Обробка введеного URL
        TextData = getattr(self.DataInput, "text", lambda: "")()
        if type(TextData) is str:
            TextData = TextData.strip()
            if TextData:
                self.NavigateUrl(TextData)
                self.DataInput.setText("")

    def SetStatus(self, Message):
        # Оновлення статусу у підвалі
        if "Status" in self.FooterBlock.Items:
            self.FooterBlock.Items["Status"].SetText(Message)

class BrowserRunner(LCARS):
    @staticmethod
    def Main() -> None:
        App = LCARS.Application.instance() or LCARS.Application(LCARS.System.Arguments)
        MainDisplay = LCARS.Display()
        Browser = NetworkInterface(MainDisplay.widget)
        Content = MainDisplay.Items["Content"].widget if "Content" in MainDisplay.Items else MainDisplay.widget
        Layout = Content.layout() or LCARS.Vertical(Content)
        Layout.addWidget(Browser.widget)
        MainDisplay.widget.resize(1024, 768)
        MainDisplay.widget.show()
        if hasattr(App, "exec"):
            LCARS.System.Exit(App.exec())

if __name__ == "__main__":
    BrowserRunner.Main()
