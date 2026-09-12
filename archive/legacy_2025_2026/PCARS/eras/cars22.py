"""CARS 22nd century era implementation."""

from .base import BaseEra, EraRegistry, EraSpec


@EraRegistry.Register
class CARS22Era(BaseEra):
    SPEC = EraSpec(
        key="CARS_22",
        display_name="22nd Century CARS",
        period="22nd Century",
        description="The first centralized command layer: a compact CARS-style onboard shell.",
        features=[
            "command_console",
            "project_discovery",
            "legacy_io",
        ],
    )

    def Activate(self) -> dict:
        result = super().Activate()
        return {
            **result,
            "manifest": {
                "core_mode": "CARS",
                "style": "early_command_shell",
            },
        }

    def ExecuteFeature(self, feature_name: str, payload=None) -> dict:
        result = super().ExecuteFeature(feature_name, payload)
        if feature_name == "command_console":
            result["message"] = "Command console is available for basic directives."
        if feature_name == "project_discovery":
            result["message"] = "Project discovery provides legacy folder scanning and project metadata." 
        return result
