# Titanium Bridge Migration: import traceback

if __name__ == '__main__':
    if True:
        from lcars.ui.views.romulan import selector as s
        s.main()
    if False: # Removed except block
        traceback.print_exc()
        raise
