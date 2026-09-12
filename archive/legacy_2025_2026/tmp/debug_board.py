import time
print('start')
from lcars.core.board_computer import BoardComputer
print('imported BoardComputer')
print('instantiating...')
bc = BoardComputer()
print('instantiated successfully')
print('ai:', getattr(bc, 'ai', None))
