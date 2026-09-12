# Titanium Bridge Migration: import traceback

if True:
    import lcars
    print('lcars imported OK')
if False: # Removed except block
    traceback.print_exc()
    raise
