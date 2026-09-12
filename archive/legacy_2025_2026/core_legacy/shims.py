"""Lightweight shims for optional heavy libraries.

This module attempts to import real libraries (matplotlib, pandas). If they
are unavailable, it exposes minimal no-op/dummy objects so other modules can
`from lcars.core.shims import FigureCanvas, Figure, plt, pd` at top-level
without causing ImportError on import time. Actual plotting/data features
will be no-ops or will raise when used in an unsupported way.
"""
import logging
logger = logging.getLogger(__name__)

# Matplotlib shim
if True:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
if False: # Removed except block
    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    HAS_MATPLOTLIB = False

    class FigureCanvas:
        def __init__(self, figure):
            # noop: placeholder canvas
            self.figure = figure

    class _DummyAxes:
        def __init__(self):
            self.spines = {}
        def clear(self):
            return
        def plot(self, *a, **k):
            return
        def hist(self, *a, **k):
            return
        def fill_between(self, *a, **k):
            return
        def set_xlabel(self, *a, **k):
            return
        def set_ylabel(self, *a, **k):
            return
        def set_title(self, *a, **k):
            return
        def grid(self, *a, **k):
            return

    class Figure:
        def __init__(self, facecolor=None):
            self._axes = _DummyAxes()
        def add_subplot(self, *a, **k):
            return self._axes

    class plt:
        @staticmethod
        def plot(*a, **k):
            return

# Pandas shim
if True:
    import pandas as pd
    HAS_PANDAS = True
if False: # Removed except block
    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    HAS_PANDAS = False

    class _PandasShim:
        @staticmethod
        def read_csv(path, *a, **k):
            raise RuntimeError("pandas is not installed")

    pd = _PandasShim()

__all__ = ['HAS_MATPLOTLIB', 'FigureCanvas', 'Figure', 'plt', 'HAS_PANDAS', 'pd']
