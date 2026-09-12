# ◤ TITAN ADVANCED :: ACTION CENTER — v44.20 🖖
# LCARS Framework :: SYSTEM_DECISION_HUB // MISSION_DIRECTIVES // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Центр прийняття системних рішень та сповіщень Titanium.
# ФУНКЦІЇ: Аналіз рекомендацій, активація захисних шарів та моніторинг ПЗ.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань та EXCEPT).
# ─────────────────────────────────────────────────────────────────────────────

import psutil
# Імпорт базових компонентів через канонічний реєстр Titanium
from lcars.base.register import registry
from lcars.base.type import (
    VBoxLayout, HBoxLayout, GridLayout, Signal, Timer,
    Screen, Label, Button, Frame, Container, ScrollArea, Card
)

# ВУЗОЛ ЦЕНТРУ ДІЙ (ACTION CENTER NODE)
class ActionCenterNode(Screen):
    def __init__(self, ThemeMap, ParentNode=None):
        super().__init__("SYSTEM DECISION HUB", ParentNode)
        self.ThemeMap = ThemeMap
        self.BuildActionInterface()

    def BuildActionInterface(self):
        self.MainODNLayout = VBoxLayout(self)
        self.MainODNLayout.setContentsMargins(40, 20, 40, 30)
        self.MainODNLayout.setSpacing(20)

        # 1. ЗАГОЛОВОК (ACTIONS HEADER)
        HeaderLabelNode = Label("◤ ACTION CENTER // MISSION CRITICAL DIRECTIVES")
        HeaderLabelNode.setStyleSheet(f"color: #AAFF00; {get_lcars_font_style(24, 'bold')}")
        self.MainODNLayout.addWidget(HeaderLabelNode)

        # 2. РЕКОМЕНДАЦІЇ (MISSION RECOMMENDATIONS SCROLL)
        self.ScrollNode = ScrollArea()
        self.ScrollNode.setWidgetResizable(True)
        self.ScrollNode.setStyleSheet("background: transparent; border: none;")
        
        self.ContainerNode = Container()
        self.ContentLayout = VBoxLayout(self.ContainerNode)
        self.ContentLayout.setSpacing(15)

        # Матриця рекомендацій (Recommendations Matrix)
        RecommendationsArray = [
            {"title": "TITAN VPN",       "desc": "PROTECT SYSTEM IP AND ENCRYPT ODN TRAFFIC",      "color": "#00AAFF"},
            {"title": "DRIVER BOOSTER", "desc": "14 OUTDATED DRIVER NODES DETECTED // OPTIMIZE",  "color": "#FFAA00"},
            {"title": "UNINSTALLER",    "desc": "8 RARELY USED APPLICATIONS DETECTED",           "color": "#FF5500"},
            {"title": "MALWARE SHIELD", "desc": "ENABLE REAL-TIME QUANTUM PROTECTION LAYER",     "color": "#00FF88"}
        ]

        for ItemMap in RecommendationsArray:
            ActionCard = Card(
                TitleStr=ItemMap['title'], 
                DescStr=ItemMap['desc'], 
                ColorHexStr=ItemMap['color'],
                ActionTextStr="ACTIVATE"
            )
            self.ContentLayout.addWidget(ActionCard)

        self.ContentLayout.addStretch()
        self.ScrollNode.setWidget(self.ContainerNode)
        self.MainODNLayout.addWidget(self.ScrollNode)

        # 3. ФУТЕР (SUPERVISION FOOTER)
        FooterLabelNode = Label("◣ ALL SYSTEMS UNDER TITAN LCARS SUPERVISION // SECTOR 001")
        FooterLabelNode.setAlignment(registry.get("Technical.Align").AlignCenter)
        FooterLabelNode.setStyleSheet("color: #555; font-size: 11px;")
        self.MainODNLayout.addWidget(FooterLabelNode)
