"""Run all corpus validations and return nonzero on failure."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "validate"))
from checks import (validate_corpus, validate_coverage, validate_duplicates, validate_encoding,
                    validate_indexes, validate_links, validate_metadata)


def run():
    results = {}
    for name, check in [("encoding", validate_encoding), ("metadata", validate_metadata),
                        ("corpus", validate_corpus), ("coverage", validate_coverage), ("duplicates", validate_duplicates),
                        ("indexes", validate_indexes), ("links", validate_links)]:
        results[name] = check()
        print(f"{name}: {'PASS' if not results[name] else 'FAIL'} ({len(results[name])} issues)")
        for issue in results[name][:20]:
            print("  " + issue)
    if any(results.values()):
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    run()
