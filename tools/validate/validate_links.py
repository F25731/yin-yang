from checks import validate_links

if __name__ == "__main__":
    errors = validate_links()
    print("PASS" if not errors else "\n".join(errors))
    raise SystemExit(bool(errors))
