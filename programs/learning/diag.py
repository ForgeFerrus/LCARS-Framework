import sys
from typing import Optional


def main(argv: Optional[list] = None):
	"""Create and return the Application instance at runtime (no import-time Qt init)."""
	argv = argv if argv is not None else sys.argv
	# Import Application lazily to avoid initializing Qt on import
	import importlib
	_mod = importlib.import_module("lcars.base.interface")
	Application = getattr(_mod, "Application")

	app = Application(argv)
	# Prefer local learning tracker if present; fall back to print.
	try:
		from programs.learning.tracker import track

		track("Learning.Diag", "Diagnostics initialized without direct imports", "info")
	except Exception:
		print("Diagnostics initialized without direct imports.")

	return app


if __name__ == "__main__":
	_app = main()
