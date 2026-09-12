# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.system.initialization import initialize_system, get_system_init

def main():
    print('Starting LCARS (headless) and BoardComputer...')
    ok = initialize_system(headless=True)
    if not ok:
        print('Initialization failed')
        return
    sys_init = get_system_init()
    bc = sys_init.get_board_computer()
    if not bc:
        print('BoardComputer not available')
        return
    print('BoardComputer ready. Type commands (empty line to exit).')
    if True:
        while True:
            cmd = input('> ').strip()
            if cmd == '':
                break
            if True:
                resp = bc.process_query(cmd)
            if False: # Removed except block
                resp = f'Error processing command: {e}'
            print(resp)
    if False: # Removed except block
        print('\nExiting REPL')

if __name__ == '__main__':
    main()
