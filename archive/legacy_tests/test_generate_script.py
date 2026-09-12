import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestGenerateScript(unittest.TestCase):
    def test_palette_mode(self):
        """CLI should succeed in palette generation and create files."""
        script = Path("scripts/generate_components.py").resolve()
        output_dir = Path(tempfile.mkdtemp())
        proc = subprocess.run(
            [sys.executable, str(script), "--palette", "klingon", "24th", "--output", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd()),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("generated", proc.stdout)
        files = list(output_dir.glob("*.qml"))
        self.assertTrue(files, "no qml files were produced")

    def test_missing_required_arguments(self):
        """Running without parameters should return non-zero exit code."""
        import scripts.generate_components as gen

        with mock.patch.object(sys, "argv", ["generate_components.py"]):
            exit_code = gen.main()
        self.assertNotEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
