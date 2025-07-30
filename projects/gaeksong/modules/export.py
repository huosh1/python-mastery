import os


def export_to_file(data, filename):
    path = f"results/{filename}"
    with open(path, "w") as f:
        f.write(data)

