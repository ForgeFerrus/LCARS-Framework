import py_compile
import glob
import sys

files = glob.glob('programs/learning/*.py')
if not files:
    print('No files found to compile')
    sys.exit(0)

ok = True
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print('Compiled', f)
    except (py_compile.PyCompileError, OSError) as e:
        print('Error compiling', f, repr(e))
        ok = False

if not ok:
    print('One or more files failed to compile')
    sys.exit(2)

print('All learning files compiled successfully')
sys.exit(0)
