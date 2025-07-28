import os

class VulnBinary:
    def __init__(self, path, exploit_cmd=None, is_exploitable=False):
        self.path = path
        self.name = os.path.basename(path)
        self.exploit_cmd = exploit_cmd
        self.is_exploitable = is_exploitable

    def __str__(self):
        status = "Yes" if self.is_exploitable else "No"
        return f"{self.name:<15} | {status:<5} | {self.path}"
