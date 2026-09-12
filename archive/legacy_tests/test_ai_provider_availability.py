# Тест доступності AI провайдерів
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lcars.service.provider import AIProvider, AIProviderManager

class TestAIProviderAvailability(unittest.TestCase):
    def setUp(self):
        self.provider = AIProvider.GetProvider()
        
    def test_provider_initialization(self):
        self.assertIsNotNone(self.provider)
        self.assertEqual(len(self.provider.Backends), 4)
        
    def test_backend_list(self):
        backend_names = [b.Name for b in self.provider.Backends]
        expected = ["qvac", "localllm", "groqwen", "mistral"]
        for name in expected:
            self.assertIn(name, backend_names)
            
    def test_groq_availability(self):
        groq_backend = None
        for backend in self.provider.Backends:
            if backend.Name == "groqwen":
                groq_backend = backend
                break
        
        self.assertIsNotNone(groq_backend)
        is_available = groq_backend.CheckAvailable()
        print(f"Groq available: {is_available}")
        
    def test_mistral_availability(self):
        mistral_backend = None
        for backend in self.provider.Backends:
            if backend.Name == "mistral":
                mistral_backend = backend
                break
        
        self.assertIsNotNone(mistral_backend)
        is_available = mistral_backend.CheckAvailable()
        print(f"Mistral available: {is_available}")
        
    def test_provider_status(self):
        status = self.provider.GetStatus()
        self.assertIn("active", status)
        self.assertIn("available", status)
        self.assertIn("backends", status)
        print(f"Provider status: {status}")
        
    def test_fallback_backend(self):
        self.provider.Initialize()
        self.assertTrue(self.provider.Initialized)
        self.assertIsNotNone(self.provider.ActiveBackend)

if __name__ == "__main__":
    unittest.main(verbosity=2)