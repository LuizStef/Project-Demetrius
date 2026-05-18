class Assistant:
    def __init__(self, name, version):
        self.name = name
        self._version = version

    def introduce(self):
        print(f"Hello! I am {self.name}, version {self._version}.")

    def __str__(self):
        return f"{self.name} v{self._version}"
