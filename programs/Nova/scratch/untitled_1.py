# ◤ NOVA LCARS SCRIPT BUFFER
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.base.default import Palette

def main():
    print('◤ LCARS SCRIPT EXECUTING 🖖')
    print(f'Active Palette: {Palette.Buttons[:3]}')

if __name__ == '__main__':
    main()
