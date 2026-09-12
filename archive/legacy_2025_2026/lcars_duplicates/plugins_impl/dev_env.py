from __future__ import annotations


def setup(api, config=None):
    """Register a simple Dev Env panel: code editor + preview + AI (mock)."""
    try:
        # Use lowercase alias if plugin passes it
        if hasattr(api, 'register_ui_integration'):
            api.register_ui_integration({'panel': 'lcars.ui.views.dev_env_panel:DevEnvPanel', 'name': 'Dev Env'})
        else:
            # fallback to PascalCase API
            api.RegisterUiIntegration({'panel': 'lcars.ui.views.dev_env_panel:DevEnvPanel', 'name': 'Dev Env'})
    except Exception:
        pass
    return {'panel': 'dev_env'}
