"""Validate that every requested metaphysics branch and its core texts are present."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import validate_coverage

errors = validate_coverage()
print(f"coverage: {'PASS' if not errors else 'FAIL'} ({len(errors)} issues)")
for issue in errors:
    print("  " + issue)
if errors:
    raise SystemExit(1)
print("PASS")
