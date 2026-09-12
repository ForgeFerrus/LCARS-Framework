from lcars.base.type import Chassis, Widget, ScrollArea, Timer
from lcars.base.interface import LCARSButton, Label, Frame
from lcars.base.default import FontStyle

from lcars.program.learning.ui.interface import LearningStation


class SettingsWidget(LearningStation):
    # Configuration and maintenance panel for the English Learning System.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress

        layout = Chassis.Vertical(self)
        self.createHeader("SYSTEM SETTINGS", layout, 1)

        scroll = ScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("#settingsScroll { background: transparent; border: none; }")

        container = Widget()
        container.setStyleSheet("background: transparent;")
        cLay = Chassis.Vertical(container)
        cLay.setContentsMargins(40, 20, 40, 20)
        cLay.setSpacing(30)

        statFrame = Frame()
        statFrame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        statLay = Chassis.Vertical(statFrame)

        lblStatTitle = Label("DATABASE STATISTICS")
        lblStatTitle.setStyleSheet(f"color: {self.theme['palette'][2]}; {FontStyle(24, 'normal')}")
        statLay.addWidget(lblStatTitle)

        stats = self.db.getStatistics()
        lblTotal = Label(f"Total Words: {stats.get('total_words', 0)}")
        lblTotal.setStyleSheet(f"color: #FFFFFF; {FontStyle(20, 'normal')}")
        statLay.addWidget(lblTotal)

        levelsText = " | ".join([f"{lvl}: {stats.get('by_level', {}).get(lvl, 0)}" for lvl in ["A1", "A2", "B1", "B2", "C1", "C2"]])
        lblLvls = Label(f"Levels: {levelsText}")
        lblLvls.setStyleSheet(f"color: #AAAAAA; {FontStyle(18, 'normal')}")
        statLay.addWidget(lblLvls)
        cLay.addWidget(statFrame)

        prgFrame = Frame()
        prgFrame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        prgLay = Chassis.Vertical(prgFrame)

        lblPrgTitle = Label("USER PROGRESS")
        lblPrgTitle.setStyleSheet(f"color: {self.theme['palette'][3]}; {FontStyle(24, 'normal')}")
        prgLay.addWidget(lblPrgTitle)

        self.btnResetPrg = LCARSButton(
            "RESET ALL PROGRESS",
            Color=self.theme.get('alert', self.theme['palette'][0]),
        )
        self.btnResetPrg.setFixedHeight(56)
        self.btnResetPrg.setStyleSheet(self.btnResetPrg.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.btnResetPrg.Clicked.connect(self.ResetProgress)
        prgLay.addWidget(self.btnResetPrg)

        self.lblResetStatus = Label("")
        self.lblResetStatus.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        prgLay.addWidget(self.lblResetStatus)
        cLay.addWidget(prgFrame)

        cLay.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    # Alias for backward compatibility
    SettingWidget = SettingsWidget

    def ResetProgress(self):
        self.db.connection.execute("DELETE FROM user_progress")
        self.db.connection.execute("DELETE FROM learning_sessions")
        self.db.connection.commit()

        self.lblResetStatus.setText("SUCCESS: PROGRESS WIPED")
        self.progress.progressUpdated.emit()
        Timer.singleShot(3000, lambda: self.lblResetStatus.setText(""))
