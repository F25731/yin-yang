from checks import validate_metadata

if __name__ == "__main__":
    errors = validate_metadata()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
