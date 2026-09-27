from checks import validate_duplicates

if __name__ == "__main__":
    errors = validate_duplicates()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
