from pathlib import Path
import json
from datetime import datetime
logFileOverride = None


def configure(logFile):
    global logFileOverride
    logFileOverride = Path(logFile) if logFile else None


def getLogFile():
    if logFileOverride is not None:
        return logFileOverride
    return Path.cwd() / "lcars" / "logs" / "learning telemetry.jsonl"


def ensureParent(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def track(source, message, level="info"):
    logPath = getLogFile()
    ensureParent(logPath)
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "source": str(source),
        "level": str(level),
        "message": str(message),
    }
    line = json.dumps(entry)
    with logPath.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
