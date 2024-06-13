import os


def delete_file(filename: str) -> bool:
    try:
        os.remove(f"{filename}")
        return True
    except FileNotFoundError:
        return False
    except PermissionError:
        return False
    except Exception as e:
        return False
