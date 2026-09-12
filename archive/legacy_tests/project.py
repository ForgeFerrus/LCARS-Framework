import unittest
import json
import tempfile
from pathlib import Path

from lcars.modules.project_manager import ProjectManager


class TestProjectManager(unittest.TestCase):
    def test_import_and_init(self):
        pm = ProjectManager(root_path=Path('.'))
        self.assertIsNotNone(pm)
        self.assertIsInstance(pm, ProjectManager)

    def test_add_remove_and_export(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pm = ProjectManager(root_path=root)

            # capture initial discovered projects (may include system paths)
            initial_names = set(pm.get_project_names())

            # create a sample project directory and add it
            proj_dir = root / 'ENX01_sample'
            proj_dir.mkdir()
            (proj_dir / 'README.md').write_text('Sample project description')

            added = pm.add_project('ENX01_sample', str(proj_dir), description='Sample')
            self.assertTrue(added)

            names_after_add = set(pm.get_project_names())
            self.assertIn('ENX01_sample', names_after_add)
            # ensure we didn't lose previously discovered projects
            self.assertTrue(initial_names.issubset(names_after_add))

            # export config to file and validate JSON structure
            out = root / 'export.json'
            pm.export_config(out)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text())
            self.assertIn('projects', data)
            # exported root_path should match the manager's root
            self.assertEqual(data.get('root_path'), str(root))

            # remove project
            removed = pm.remove_project('ENX01_sample')
            self.assertTrue(removed)
            self.assertNotIn('ENX01_sample', pm.get_project_names())


if __name__ == '__main__':
    unittest.main()
