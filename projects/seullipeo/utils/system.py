import subprocess

def find_suid_binaries():
    """
    Scan les fichiers SUID sur le système.
    Retourne une liste de chemins absolus.
    """
    result = subprocess.run(
        ["find", "/", "-perm", "-4000", "-type", "f"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    return result.stdout.strip().split("\n")


def get_current_user():
    """
    Retourne le nom de l'utilisateur courant.
    """
    try:
        return subprocess.check_output("whoami", shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return "unknown"


def is_root():
    """
    Retourne True si l'utilisateur est root.
    """
    return get_current_user() == "root"


def exec_command(cmd):
    """
    Exécute une commande shell simple.
    """
    return subprocess.run(cmd, shell=True)
