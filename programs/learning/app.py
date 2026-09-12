# Compatibility shim.
# Canonical implementation is programs.learning.English.

from programs.learning.English import LinguisticApp, runEnglish


def runApp() -> int:
    return runEnglish()


if __name__ == "__main__":
    raise SystemExit(runApp())
