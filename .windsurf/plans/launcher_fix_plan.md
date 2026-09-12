# Launcher Fix Plan

The main issue is that the launcher isn't working properly. Scripts have been moved to scripts/ directory, but project_explorer.py has mixed implementations and the launcher flow is broken.

## Current State Analysis

1. **Scripts moved** - LCARS Script files are now in scripts/ directory (good)
2. **Project Explorer confused** - Multiple implementations mixed together
3. **Launcher broken** - start_lcars.py exists but desktop integration fails
4. **Design overload** - Too many design options, need single entry point

## Immediate Priority: Fix Launcher

The launcher must work first before any design or testing. Focus on:

1. **Fix project_explorer.py** - Clean single implementation that works
2. **Complete desktop.py integration** - Make launch_project_explorer() functional
3. **Verify launcher flow** - start_lcars.py → LCARSDesktop → Project Explorer
4. **Remove complexity** - One working design, not multiple options

## Implementation Steps

1. Clean project_explorer.py to single working implementation
2. Fix desktop.py launch_project_explorer() method
3. Test launcher: python start_lcars.py → desktop → PROJECTS button
4. Verify Project Explorer opens and functions
5. Only then consider design improvements

The goal is working launcher first, everything else secondary.
