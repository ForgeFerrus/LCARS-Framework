import sys
from lcars.core.system import MasterSystem
from lcars.themes.palette import LCARSEra


def launch_22nd():
    # Build 22nd century minimal shell
    print('Launching LCARS 22nd Century System')
    system = MasterSystem(sys.argv)
    system._era = LCARSEra.COMS_22ND
    system.startup()
    return system
