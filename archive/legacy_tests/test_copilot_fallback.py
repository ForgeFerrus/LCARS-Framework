import unittest
from pathlib import Path
from lcars.core.AI_agent import Copilot


class TestCopilotFallback(unittest.TestCase):
    def setUp(self):
        # Force fallback (no LLM client) and use Path for project_root
        self.c = Copilot(project_root=Path('.'))
        self.c._client = None

    def test_structure(self):
        res = self.c.run('structure')
        self.assertIn('PROJECT: LCARS Framework', res)

    def test_read_file_fallback(self):
        res = self.c.run('read lcars/core/board_computer.py')
        self.assertTrue(res.startswith('FILE:') or 'READ ERROR' in res)
