# Простий тест наявності AI бібліотек
import sys

print("Checking AI libraries availability...")

try:
    import groq
    print("✅ groq library installed")
    print(f"   Version: {groq.__version__ if hasattr(groq, '__version__') else 'unknown'}")
except ImportError:
    print("❌ groq library NOT installed")

try:
    import mistralai
    print("✅ mistralai library installed")
    print(f"   Version: {mistralai.__version__ if hasattr(mistralai, '__version__') else 'unknown'}")
except ImportError:
    print("❌ mistralai library NOT installed")

try:
    import transformers
    print("✅ transformers library installed")
    print(f"   Version: {transformers.__version__ if hasattr(transformers, '__version__') else 'unknown'}")
except ImportError:
    print("❌ transformers library NOT installed")

try:
    import requests
    print("✅ requests library installed")
    print(f"   Version: {requests.__version__ if hasattr(requests, '__version__') else 'unknown'}")
except ImportError:
    print("❌ requests library NOT installed")

print("\nPython version:", sys.version)
print("Python executable:", sys.executable)