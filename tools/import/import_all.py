"""Rebuild from already checked-out source trees; use --fetch for pinned network sync."""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest


def fetch(source):
    sid = source["id"]
    if source["type"] == "mediawiki":
        command = [sys.executable, str(ROOT / source["importer"]), "--fetch"]
        if sid not in ("wikisource-yuewei", "wikisource-liaozhai", "wikisource-zengshan", "wikisource-qimenbaojian"):
            command += ["--work", "meihua" if sid.endswith("meihua") else "huangjince"]
        subprocess.run(command, check=True)
        return
    dirname = sid.split("-", 1)[1] if sid.startswith("kanripo-") else ("xml-p5" if sid == "cbeta-xml-p5" else sid)
    path = ROOT / ".work" / dirname
    if not path.exists():
        args = ["git", "clone", "--depth", "1"]
        if sid == "cbeta-xml-p5":
            args += ["--filter=blob:none", "--no-checkout"]
        args += [source["url"] + ".git", str(path)]
        subprocess.run(args, check=True)
    subprocess.run(["git", "-C", str(path), "fetch", "--depth", "1", "origin", source["imported_commit"]], check=True)
    if sid == "cbeta-xml-p5":
        subprocess.run(["git", "-C", str(path), "sparse-checkout", "init", "--cone"], check=True)
        subprocess.run(["git", "-C", str(path), "sparse-checkout", "set", "T"], check=True)
    subprocess.run(["git", "-C", str(path), "checkout", "--detach", source["imported_commit"]], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="source ID; omit to rebuild all enabled sources")
    parser.add_argument("--fetch", action="store_true", help="fetch pinned upstream commit/revision")
    args = parser.parse_args()
    manifest = read_manifest()
    selected = [manifest[args.source]] if args.source else list(manifest.values())
    failures = []
    for source in selected:
        sid = source["id"]
        if not source["enabled"]:
            print(f"SKIP {sid}: license not verified")
            continue
        try:
            if args.fetch:
                fetch(source)
            if sid.startswith("kanripo-"):
                code = sid.split("-", 1)[1]
                script = "import_kanripo_extra.py" if source["importer"].endswith("extra.py") else "import_kanripo.py"
                command = [sys.executable, str(ROOT / "tools/import" / script), code]
            elif sid == "kr5-corpus":
                command = [sys.executable, str(ROOT / "tools/import/import_kr5.py")]
            elif sid == "cbeta-xml-p5":
                command = [sys.executable, str(ROOT / "tools/import/import_cbeta.py")]
            elif sid == "wikisource-yuewei":
                command = [sys.executable, str(ROOT / "tools/import/import_yuewei.py")]
            elif sid == "wikisource-liaozhai":
                command = [sys.executable, str(ROOT / "tools/import/import_liaozhai.py")]
            elif sid == "wikisource-zengshan":
                command = [sys.executable, str(ROOT / "tools/import/import_zengshan.py")]
            elif sid == "wikisource-qimenbaojian":
                command = [sys.executable, str(ROOT / "tools/import/import_qimenbaojian.py")]
            else:
                continue  # MediaWiki works share one pinned importer, called below.
            subprocess.run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            failures.append(f"{sid}: {exc}")
    if not args.source or args.source in ("wikisource-meihua", "wikisource-huangjince"):
        try:
            work = "all" if not args.source else ("meihua" if args.source.endswith("meihua") else "huangjince")
            subprocess.run([sys.executable, str(ROOT / "tools/import/import_wikisource.py"), "--work", work], check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            failures.append(f"wikisource: {exc}")
    (ROOT / "reports/IMPORT_FAILED_ITEMS.txt").write_text("\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("IMPORT PASS")


if __name__ == "__main__":
    main()
