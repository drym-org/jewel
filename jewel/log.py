def log(name, message):
    """ We only log when a name is provided. """
    if name:
        print(f"[{name}] {message}")
