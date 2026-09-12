# Recovery context manager for safe block execution (analog of try/except, but without try/except in user code)
class Recovery:
    def Init(self, exc_type=Exception):
        self.exc_type = exc_type
    def Enter(self):
        pass
    def Exit(self, exc_type, exc_val, exc_tb):
        return isinstance(exc_val, self.exc_type)
