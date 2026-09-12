# ◤ TITANIUM TACTICAL COMLINK — v24.2 // DIRECT-LINK MASTER 🖖
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Повнофункціональний месенджер із прямим імпортом логіки.
# ПРОТОКОЛ: Direct-Import // Zero-Registry // Stable-Matrix.
# ───────────────────────────────────────────────────────────────

import sys, os, time
from lcars.base.register import registry
from lcars.base.type import Directive, LCARS, Matrix, Visual, ODN, Signal, Primitives

# ПРЯМИЙ ІМПОРТ КОМПОНЕНТІВ (Обхід проблем реєстру)
from lcars.base.components import LCARSPadd, LCARSButton, LCARSLabel
from lcars.modules.communication import GetCommController, ContactNode

class TacticalComlink(LCARSPadd):
    def __init__(self, ParentNode=None):
        # Ініціалізація без закладання на registry.get
        super().__init__("TITANIUM COMLINK", color="#336699", ParentNode=ParentNode)
        self.resize(1150, 800)
        
        # ОЧИЩЕННЯ РАМИ
        for Node in [self.TopElbow, self.BottomElbow, self.TopBar, self.BottomBar, self.LeftSideBar]:
            Node.hide()
            
        self.viewport().setStyleSheet("background: #000000; border: none;")
        self.MainLayout = self.ViewportLayout
        self.MainLayout.setContentsMargins(15, 15, 15, 15)
        self.MainLayout.setSpacing(10)
        
        # СТАН
        self.CommNode = GetCommController()
        self.ActiveTarget = None

        # 1. КОМАНДНА ШАПКА
        self.HeaderODN = ODN.Horizontal()
        self.TitleLabel = LCARSLabel("◤ SUBSPACE COMLINK // TACTICAL NODE // MASTER LINK", FontSizeVal=16, ColorHexStr="#99CCFF")
        self.BtnRefresh = LCARSButton("SYNC SYSTEM", color="#D37445", shape="rect")
        self.BtnRefresh.clicked.connect(self.LoadRegistry)
        
        self.HeaderODN.addWidget(self.TitleLabel, 1)
        self.HeaderODN.addWidget(self.BtnRefresh, 2)
        self.MainLayout.addLayout(self.HeaderODN)

        # 2. ОСНОВНИЙ ВЕРКБЕНЧ
        self.WorkbenchODN = ODN.Horizontal()
        self.WorkbenchODN.setSpacing(15)
        self.MainLayout.addLayout(self.WorkbenchODN, 1)

        # САЙДБАР РЕЄСТРУ (Side Matrix)
        self.SidebarNode = Matrix(self)
        self.SidebarNode.setMinimumWidth(300)
        self.SidebarNode.setStyleSheet("background: #050510; border-right: 2px solid #333; border-radius: 8px;")
        self.SidebarLayout = ODN.Vertical(self.SidebarNode)
        self.SidebarLayout.setContentsMargins(10, 10, 10, 10)
        self.SidebarLayout.setSpacing(8)
        
        self.SidebarLayout.addWidget(LCARSLabel("◤ COMLINK REGISTRY", FontSizeVal=10, ColorHexStr="white"))
        self.ContactButtons = []
        self.WorkbenchODN.addWidget(self.SidebarNode)

        # ПАНЕЛЬ ПЕРЕДАЧІ (Feed Matrix)
        self.FeedNode = Matrix(self)
        self.FeedLayout = ODN.Vertical(self.FeedNode)
        self.FeedLayout.setSpacing(12)
        
        self.LogTerminal = Visual.Text()
        self.LogTerminal.setReadOnly(True)
        self.LogTerminal.setStyleSheet(
            "background: #000000; border: 1px solid #1A2535; color: #99CCFF; "
            "font-family: 'LCARS'; font-size: 14pt; padding: 15px; border-radius: 12px;"
        )
        self.FeedLayout.addWidget(self.LogTerminal, 1)
        
        # ВВОД ПОВІДОМЛЕННЯ
        self.UplinkODN = ODN.Horizontal()
        from PyQt6.QtWidgets import QLineEdit
        self.InputArea = QLineEdit()
        self.InputArea.setPlaceholderText("ENTER SUBSPACE ENCODING...")
        self.InputArea.setStyleSheet(
            "background: #111; color: white; border: 1px solid #444; "
            "height: 60px; font-family: 'LCARS'; font-size: 16pt; padding: 0 15px; border-radius: 8px;"
        )
        self.BtnTransmit = LCARSButton("TRANSMIT", color="#D37445", shape="rect")
        self.BtnTransmit.setFixedWidth(160)
        self.BtnTransmit.clicked.connect(self.SendMessage)
        
        self.UplinkODN.addWidget(self.InputArea, 1)
        self.UplinkODN.addWidget(self.BtnTransmit)
        self.FeedLayout.addLayout(self.UplinkODN)
        
        self.WorkbenchODN.addWidget(self.FeedNode, 1)

        # 3. ТРЕЙ СТАНУ
        self.StatusLabel = LCARSLabel("STATUS: ODN LINK ACTIVE // READY", ColorHexStr="#666666", FontSizeVal=10)
        self.MainLayout.addWidget(self.StatusLabel)

        self.LoadRegistry()

    def LoadRegistry(self):
        # ◤ ТАКТИЧНА СИНХРОНІЗАЦІЯ
        for Bt in self.ContactButtons:
            Bt.setParent(None)
            Bt.deleteLater()
        self.ContactButtons = []
        
        Contacts = self.CommNode.SearchContacts("")
        if not Contacts:
             self.CommNode.AddContact(ContactNode(Name="STARFLEET COMMAND", Faction="FEDERATION"))
             self.CommNode.AddContact(ContactNode(Name="KLINGON HIGH COUNCIL", Faction="KLINGON"))
             self.CommNode.AddContact(ContactNode(Name="SPOCK", Faction="VULCAN"))
             Contacts = self.CommNode.SearchContacts("")

        self.StatusLabel.setText(f"STATUS: ENCRYPTED // LINK: {len(Contacts)} TACTICAL NODES")

        for C in Contacts:
            # Динамічний колір за фракцію
            Col = "#6699CC"
            if C.Faction and "KLINGON" in C.Faction.upper(): Col = "#CC0000"
            elif C.Faction and "VULCAN" in C.Faction.upper(): Col = "#F9A111"
            
            Bt = LCARSButton(f"◤ {C.Name}", ColorHexStr=Col, shape="rect")
            Bt.setMinimumHeight(55)
            Bt.clicked.connect(lambda ch, target=C: self.SelectContact(target))
            
            self.ContactButtons.append(Bt)
            self.SidebarLayout.addWidget(Bt)
            Bt.show()
            
        self.SidebarLayout.addStretch(1)
        self.update()

    def SelectContact(self, C):
        self.ActiveTarget = C
        self.TitleLabel.setText(f"COMLINK LINK // {C.Name} // SECURE")
        self.RefreshMessages()

    def RefreshMessages(self):
        if not self.ActiveTarget: return
        self.LogTerminal.clear()
        Msgs = self.CommNode.GetMessages(self.ActiveTarget.Name)
        for M in Msgs:
            T = time.strftime('%H:%M:%S', time.localtime(M.Timestamp))
            Prefix = ">>>" if M.Sender == self.ActiveTarget.Name else "<<<"
            self.LogTerminal.appendPlainText(f"{Prefix} [{T}] {M.Sender}: {M.Content}")

    def SendMessage(self):
        Txt = self.InputArea.text()
        if not Txt or not self.ActiveTarget: return
        self.CommNode.SendSubspaceMessage("COMMANDER", self.ActiveTarget.Name, Txt)
        self.InputArea.clear()
        self.RefreshMessages()

if __name__ == "__main__":
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    Comm = TacticalComlink()
    Comm.show()
    sys.exit(AppInst.exec())
