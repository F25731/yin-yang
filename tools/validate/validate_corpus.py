from checks import validate_corpus

if __name__ == "__main__":
    errors = validate_corpus()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
