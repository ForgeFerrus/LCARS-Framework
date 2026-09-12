EarlyLogsArray: list[str] = []

class PreBootCatcher:
    def write(self, value: str):
        if value and value.strip():
            EarlyLogsArray.append(value)

    def flush(self):
        pass

    def reconfigure(self, **kwargs):
        pass
