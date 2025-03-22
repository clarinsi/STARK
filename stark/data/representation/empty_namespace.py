class EmptyNamespace:
    def __getattr__(self, name):
        return False