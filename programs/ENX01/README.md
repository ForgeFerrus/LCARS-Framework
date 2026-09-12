ENX01 program (LCARS `programs` proxy)

This folder exposes ENX01 as a LCARS program. The scripts here proxy to the
actual Geant4 project located in `Geant4/Enterprise/ENX01` within the workspace.

Usage (PowerShell):

    .\build.bat        # forwards to Geant4/Enterprise/ENX01/build_ENX01.bat
    .\run.bat          # forwards to Geant4/Enterprise/ENX01/run_ENX01.bat

If the Geant4 project is stored elsewhere, update the proxy scripts or run
the helpers directly in `Geant4/Enterprise/ENX01`.
