from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.interface import Panel, Segment

class ConsolePanel(Panel):
    def __init__(self, Parent=None):
        super().__init__(Id="ConsolePanel")
        self.Parent = Parent