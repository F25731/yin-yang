from checks import validate_indexes

if __name__ == "__main__":
    errors = validate_indexes()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
