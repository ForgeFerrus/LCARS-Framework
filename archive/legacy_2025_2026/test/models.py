from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import unittest
import sysconfig
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = Path(__file__).resolve().parent
sys.path[:] = [entry for entry in sys.path if Path(entry or ".").resolve() != TEST_DIR]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

signal_path = Path(sysconfig.get_path("stdlib")) / "signal.py"
signal_spec = importlib.util.spec_from_file_location("_lcars_stdlib_signal", signal_path)
if signal_spec is not None and signal_spec.loader is not None:
    stdlib_signal = importlib.util.module_from_spec(signal_spec)
    sys.modules[signal_spec.name] = stdlib_signal
    signal_spec.loader.exec_module(stdlib_signal)
    sys.modules["signal"] = stdlib_signal


PROMPT = "Reply with exactly: READY"
SYSTEM_PROMPT = "You are a minimal LCARS diagnostic backend."
CONTEXT = "LCARS model suitability probe."
SELECTED_BACKENDS: set[str] | None = None
SELECTED_MODELS: set[str] | None = None


def load_provider_module():
    original_run = subprocess.run
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name, *args, **kwargs):
        if name in {"groq", "mistralai"}:
            return None
        return original_find_spec(name, *args, **kwargs)

    subprocess.run = lambda *args, **kwargs: None
    importlib.util.find_spec = fake_find_spec
    try:
        return importlib.import_module("lcars.service.provider")
    finally:
        subprocess.run = original_run
        importlib.util.find_spec = original_find_spec


def text_preview(value: Any, limit: int = 180) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    text = " ".join(text.split())
    text = text.encode("ascii", "replace").decode("ascii")
    return text[:limit]


def is_failure_text(value: Any) -> bool:
    text = text_preview(value, 500).lower()
    if not text:
        return True
    markers = (
        "error",
        "unavailable",
        "not loaded",
        "not initialized",
        "model loading failed",
        "connection error",
    )
    return any(marker in text for marker in markers)


def board_fit_for(backend: str, model: str) -> str:
    if backend == "hf_local":
        return "local offline fallback; lightweight but weak"
    if backend == "gemma":
        return "local offline model family; heavier, better only if hardware has enough memory"
    if backend == "groqwen":
        return "remote API; not suitable for isolated board operation"
    if backend == "mistral":
        return "remote API; not suitable for isolated board operation"
    if backend == "nova":
        return "adapter-driven; suitability depends on the adapter implementation"
    return "unknown"


def verdict_for(backend: str, available: bool, generated: bool, latency_ms: int | None) -> str:
    if not available:
        return "OFFLINE"
    if not generated:
        return "BROKEN"
    if latency_ms is None:
        return "UNKNOWN"
    if backend in {"hf_local", "nova"} and latency_ms <= 1000:
        return "GOOD"
    if backend == "gemma" and latency_ms <= 3000:
        return "GOOD"
    if latency_ms <= 5000:
        return "SLOW"
    return "TOO SLOW"


def hf_probe(module, model_name: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "backend": "hf_local",
        "model": model_name,
        "available": False,
        "generated": False,
        "latency_ms": None,
        "preview": "",
        "board_fit": board_fit_for("hf_local", model_name),
        "verdict": "OFFLINE",
        "notes": "",
    }

    if importlib.util.find_spec("transformers") is None or importlib.util.find_spec("torch") is None:
        result["notes"] = "transformers/torch missing"
        return result

    transformers = importlib.import_module("transformers")
    torch = importlib.import_module("torch")
    AutoTokenizer = getattr(transformers, "AutoTokenizer")
    AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
        inputs = tokenizer.encode(PROMPT, return_tensors="pt")
        started = time.perf_counter()
        with torch.no_grad():
            outputs = model.generate(inputs, max_length=inputs.shape[1] + 8)
        elapsed = int((time.perf_counter() - started) * 1000)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        result["available"] = True
        result["generated"] = bool(response)
        result["latency_ms"] = elapsed
        result["preview"] = text_preview(response)
        if is_failure_text(response):
            result["generated"] = False
            result["notes"] = "model returned failure-like text"
        result["verdict"] = verdict_for("hf_local", True, result["generated"], elapsed)
    except Exception as exc:
        result["notes"] = str(exc)
    return result


def instantiate_backend(module, backend: str, model: str | None = None):
    if backend == "hf_local":
        return module.LocalAI()
    if backend == "gemma":
        return module.GemmaSpark(model=model or "gemma4-4b", enableThinking=False)
    if backend == "groqwen":
        return module.GROQwen(model=model or "mixtral-8x7b-32768")
    if backend == "mistral":
        return module.Mistral(model=model or "mistralai/Mistral-7B-Instruct-v0.2")
    if backend == "nova":
        return module.Nova()
    raise ValueError(f"Unknown backend: {backend}")


def probe_backend_model(module, backend: str, model: str | None = None, instance: Any | None = None) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "backend": backend,
        "model": model or "",
        "available": False,
        "generated": False,
        "latency_ms": None,
        "preview": "",
        "board_fit": board_fit_for(backend, model or backend),
        "verdict": "OFFLINE",
        "notes": "",
    }

    if instance is None:
        instance = instantiate_backend(module, backend, model)
    available = bool(instance.checkAvailable())
    row["available"] = available
    if not available:
        row["notes"] = "backend not available"
        return row

    if backend == "gemma" and model and hasattr(instance, "switchModel"):
        instance.switchModel(model)
    elif backend in {"groqwen", "mistral"} and model is not None:
        setattr(instance, "model", model)

    started = time.perf_counter()
    try:
        if backend == "gemma":
            response = instance.generate(PROMPT, SYSTEM_PROMPT, CONTEXT, 48)
        else:
            response = instance.generate(PROMPT, SYSTEM_PROMPT, CONTEXT)
        elapsed = int((time.perf_counter() - started) * 1000)
        row["generated"] = not is_failure_text(response)
        row["latency_ms"] = elapsed
        row["preview"] = text_preview(response)
        if not row["generated"]:
            row["notes"] = "generation returned error-like text"
        row["verdict"] = verdict_for(backend, True, row["generated"], elapsed)
    except Exception as exc:
        row["latency_ms"] = int((time.perf_counter() - started) * 1000)
        row["notes"] = str(exc)
    return row


def collect_model_diagnostics() -> List[Dict[str, Any]]:
    module = load_provider_module()
    rows: List[Dict[str, Any]] = []

    provider = module.AIProviderManager()
    gemma_instance = None
    groq_instance = None
    mistral_instance = None
    for backend in provider.backends:
        backend_name = backend.name
        if SELECTED_BACKENDS is not None and backend_name not in SELECTED_BACKENDS:
            continue
        if backend_name == "hf_local":
            for model_name in backend.getAvailableModels():
                if SELECTED_MODELS is not None and model_name not in SELECTED_MODELS:
                    continue
                rows.append(hf_probe(module, model_name))
        elif backend_name == "gemma":
            if gemma_instance is None:
                gemma_instance = module.GemmaSpark(model="gemma4-4b", enableThinking=False)
            for model_name in backend.getAvailableModels():
                if SELECTED_MODELS is not None and model_name not in SELECTED_MODELS:
                    continue
                rows.append(probe_backend_model(module, backend_name, model_name, instance=gemma_instance))
        elif backend_name == "groqwen":
            if groq_instance is None:
                groq_instance = module.GROQwen(model="mixtral-8x7b-32768")
            for model_name in backend.getInfo().get("models", []):
                if SELECTED_MODELS is not None and model_name not in SELECTED_MODELS:
                    continue
                rows.append(probe_backend_model(module, backend_name, model_name, instance=groq_instance))
        elif backend_name == "mistral":
            if mistral_instance is None:
                mistral_instance = module.Mistral(model="mistralai/Mistral-7B-Instruct-v0.2")
            for model_name in backend.getInfo().get("models", []):
                if SELECTED_MODELS is not None and model_name not in SELECTED_MODELS:
                    continue
                rows.append(probe_backend_model(module, backend_name, model_name, instance=mistral_instance))
        elif backend_name == "nova":
            rows.append(probe_backend_model(module, backend_name, None))

    return rows


def print_report(rows: List[Dict[str, Any]]) -> None:
    header = f"{'BACKEND':<10} {'MODEL':<28} {'AVAIL':<5} {'GEN':<3} {'MS':<6} {'VERDICT':<9} {'FIT':<38} PREVIEW"
    print(header)
    print("-" * len(header))
    for row in rows:
        model = row["model"] or "-"
        ms = "-" if row["latency_ms"] is None else str(row["latency_ms"])
        preview = row["preview"] or row["notes"] or "-"
        print(
            f"{row['backend']:<10} "
            f"{model:<28.28} "
            f"{str(row['available']):<5} "
            f"{str(row['generated']):<3} "
            f"{ms:<6} "
            f"{row['verdict']:<9} "
            f"{row['board_fit']:<38.38} "
            f"{preview}"
        )


class TestAIModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_provider_module()

    def test_provider_inventory(self):
        manager = self.module.AIProviderManager()
        names = [backend.name for backend in manager.backends]
        self.assertEqual(names, ["nova", "hf_local", "gemma", "groqwen", "mistral"])

    def test_backend_surface(self):
        manager = self.module.AIProviderManager()
        for backend in manager.backends:
            with self.subTest(backend=backend.name):
                self.assertTrue(hasattr(backend, "checkAvailable"))
                self.assertTrue(hasattr(backend, "generate"))
                self.assertTrue(hasattr(backend, "getInfo"))
                self.assertTrue(hasattr(backend, "getAvailableModels"))

    def test_model_matrix(self):
        rows = collect_model_diagnostics()
        print_report(rows)

        self.assertGreater(len(rows), 0)
        for row in rows:
            with self.subTest(backend=row["backend"], model=row["model"]):
                self.assertIn("board_fit", row)
                self.assertIn("verdict", row)
                self.assertIn("notes", row)
                if row["backend"] in {"hf_local", "gemma"} and row["available"]:
                    self.assertTrue(row["generated"], row["notes"] or row["preview"] or "generation failed")

    def test_status_report(self):
        manager = self.module.AIProviderManager()
        status = manager.getStatus()
        self.assertIn("active", status)
        self.assertIn("initialized", status)
        self.assertIn("is_ai", status)
        self.assertIn("backends", status)
        self.assertIsInstance(status["backends"], list)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LCARS AI model diagnostics")
    parser.add_argument(
        "--backend",
        action="append",
        choices=["nova", "hf_local", "gemma", "groqwen", "mistral"],
        help="Limit diagnostics to selected backend(s). Can be repeated.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Limit diagnostics to selected model name(s). Can be repeated.",
    )
    parser.add_argument("--full", action="store_true", help="Run the full diagnostics matrix")
    args = parser.parse_args(argv)

    global SELECTED_BACKENDS, SELECTED_MODELS
    if args.backend:
        SELECTED_BACKENDS = set(args.backend)
    elif args.full:
        SELECTED_BACKENDS = None
    else:
        SELECTED_BACKENDS = {"hf_local", "gemma"}

    if args.model:
        SELECTED_MODELS = set(args.model)
    else:
        SELECTED_MODELS = None

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAIModels)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
