"""Inventory unlicensed upstreams without redistributing their text."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_json

KEYWORDS = ("搜神", "山海", "聊齋", "聊斋", "異記", "异记", "博物", "夷堅", "夷坚",
            "太平廣記", "太平广记", "志怪", "子平", "六壬", "六爻", "梅花", "奇門", "奇门",
            "太乙", "風水", "风水", "葬經", "葬经", "相法", "相術", "相术", "卜筮", "紫微", "易經", "易经")


def run(source_id):
    source = read_manifest()[source_id]
    base = ROOT / ".work" / source_id
    if not base.exists():
        raise FileNotFoundError(f"missing {base}")
    text = subprocess.check_output(["git", "-c", "core.quotePath=false", "-C", str(base),
                                    "ls-tree", "-r", "--name-only", "HEAD"])
    paths = text.decode("utf-8").splitlines()
    candidates = [p for p in paths if any(word in p for word in KEYWORDS)]
    data = {"source_id": source_id, "commit": source["imported_commit"],
            "files_in_tree": len(paths), "candidate_paths": candidates,
            "decision": "No corpus text imported: no verified republication license for the dataset"}
    write_json(ROOT / "sources/provenance" / f"{source_id}-inventory.json", data)
    print(f"INVENTORIED {source_id}: {len(candidates)} candidate paths; text withheld")


if __name__ == "__main__":
    run(sys.argv[1])
