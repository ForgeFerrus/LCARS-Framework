import unittest

class TestArchitectImport(unittest.TestCase):
    def test_import_architect(self):
        # module should import without error and provide ArchitectCanvas class
        import importlib
        m = importlib.import_module('lcars.engineering.architect')
        self.assertTrue(hasattr(m, 'ArchitectCanvas'))
        self.assertTrue(hasattr(m, 'IsolinearArchitect'))

if __name__ == '__main__':
    unittest.main()
