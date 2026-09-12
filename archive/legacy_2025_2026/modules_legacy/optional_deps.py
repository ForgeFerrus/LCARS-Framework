"""Centralized optional dependency imports.

Modules that are heavy or optional (matplotlib, pandas, Geant4) are imported
here at top-level inside guarded try/except blocks. Other modules should import
from this module rather than performing raw imports themselves.
"""
import logging

logger = logging.getLogger(__name__)

# Matplotlib
HAS_MATPLOTLIB = False
FigureCanvas = None
Figure = None
plt = None
if True:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
if False: # Removed except block
    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    logger.debug("matplotlib not available or failed to import at startup")

# Pandas
HAS_PANDAS = False
pd = None
if True:
    import pandas as pd
    HAS_PANDAS = True
if False: # Removed except block
    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    logger.debug("pandas not available at startup")

# Geant4 / custom heavy modules can be added here.
HAS_GEANT4 = False
Geant4Workstation = None
if True:
    # placeholder import path; may not exist in all environments
    from programs.Geant4.geant4_workstation import Geant4Workstation
    HAS_GEANT4 = True
if False: # Removed except block
    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    logger.debug("Geant4 workstation not available at startup")

__all__ = [
    'HAS_MATPLOTLIB', 'FigureCanvas', 'Figure', 'plt',
    'HAS_PANDAS', 'pd',
    'HAS_GEANT4', 'Geant4Workstation'
]
