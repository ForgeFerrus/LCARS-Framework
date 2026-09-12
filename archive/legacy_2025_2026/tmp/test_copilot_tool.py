import os, sys
from pathlib import Path
sys.path.insert(0, os.getcwd())
from lcars.core.copilot import Copilot

c = Copilot(project_root=Path.cwd())
print('hello:', c.run('hello'))

prompt = '[[TOOL_CALL]] {"name": "read_file", "arguments": {"path": "README.md"}}'
print('tool call response:')
print(c.run(prompt))
