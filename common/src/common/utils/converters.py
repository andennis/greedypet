def str_to_bool(val: str | None) -> bool:
    if not val:
        return False
    lw_val = val.lower()
    if lw_val in {'1', 'on', 't', 'true', 'y', 'yes'}:
        return True
    if lw_val in {'0', 'off', 'f', 'false', 'n', 'no'}:
        return False
    raise ValueError(f"Value '{val}' is not boolean value")

