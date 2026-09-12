import unittest
import tempfile
from pathlib import Path
import re

from lcars.engineering.generators.component_factory import LcarsComponentFactory, logger


class TestComponentFactory(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.output = Path(self.tempdir.name)
        self.factory = LcarsComponentFactory(output_dir=str(self.output))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_generate_component_creates_file(self):
        path = self.factory.generate_component(
            component_type="button",
            name="testbtn",
            image_path="/path/to/img.svg",
            color="#ABCDEF",
            text="HELLO",
            width=100,
            height=40,
        )
        self.assertTrue(Path(path).exists())
        content = Path(path).read_text()
        # verify that template variables were substituted
        self.assertIn("testbtn", content)
        self.assertIn("HELLO", content)
        self.assertIn("#ABCDEF", content)
        self.assertIn("/path/to/img.svg", content)

    def test_generate_klingon_button_returns_path(self):
        path = self.factory.generate_klingon_button(
            name="kling1",
            color="#660000",
            text="KLING",
            era="24th",
        )
        self.assertTrue(Path(path).exists())
        content = Path(path).read_text()
        self.assertIn("kling1", content)
        self.assertIn("KLING", content)

    def test_generate_from_palette_uses_colors(self):
        # monkeypatch get_faction_colors to predictable palette
        from lcars.themes.theme import get_faction_colors
        orig = get_faction_colors

        def fake_palette(faction, era):
            return {"button_colors": ["#111111", "#222222"]}

        try:
            import lcars.themes.theme as theme_mod
            theme_mod.get_faction_colors = fake_palette
            files = self.factory.generate_from_palette(
                faction="klingon",
                era="24th",
                component_types=["button", "panel"],
            )
            self.assertEqual(len(files), 2)
            for p in files:
                self.assertTrue(Path(p).exists())
        finally:
            import lcars.themes.theme as theme_mod
            theme_mod.get_faction_colors = orig

    def test_logging_on_generate(self):
        with self.assertLogs(logger, level="INFO") as cm:
            self.factory.generate_component(
                component_type="panel",
                name="logtest",
                image_path="x.png",
            )
        self.assertTrue(any("Компонент logtest.qml" in m for m in cm.output))

    def test_ukrainian_comments_exist(self):
        # ensure the module contains at least one Ukrainian comment marker
        import inspect
        src = inspect.getsource(LcarsComponentFactory)
        self.assertRegex(src, r"#.*Пояснення|#.*генер")


if __name__ == "__main__":
    unittest.main()
