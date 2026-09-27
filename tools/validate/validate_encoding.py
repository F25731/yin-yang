from checks import validate_encoding

if __name__ == "__main__":
    errors = validate_encoding()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
