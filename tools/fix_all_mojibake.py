from pathlib import Path
import json
import sys

try:
    from ftfy import fix_text
except ImportError:
    fix_text = None


ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {
    ".json", ".html", ".htm", ".md", ".txt", ".py",
    ".js", ".css", ".yml", ".yaml", ".xml", ".csv"
}

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".idea", ".vscode"
}

# Known mojibake and half-repaired mojibake patterns found in this repo.
REPLACEMENTS = {
    # Full mojibake forms
    "鈥檚": "’s",
    "鈥檛": "’t",
    "鈥檙": "’r",
    "鈥檝": "’v",
    "鈥檒": "’l",
    "鈥檇": "’d",
    "鈥榬": "’r",

    "鈥淎": "“A",
    "鈥淭": "“T",
    "鈥淐": "“C",
    "鈥淚": "“I",
    "鈥淲": "“W",
    "鈥淪": "“S",
    "鈥渁": "“a",
    "鈥渢": "“t",
    "鈥渃": "“c",
    "鈥渋": "“i",
    "鈥渨": "“w",
    "鈥渟": "“s",

    "鈥濃": "”",
    "鈥?": "”",
    "鈥": "’",

    "鈥揅": "–C",
    "鈥揢": "–U",
    "鈥揑": "–I",
    "鈥揚": "–P",
    "鈥揇": "–D",
    "鈥揙": "–O",
    "鈥揝": "–S",
    "鈥揟": "–T",
    "鈥揗": "–M",
    "鈥揘": "–N",
    "鈥揥": "–W",
    "鈥揂": "–A",
    "鈥攔": "—r",
    "鈥斺": "—",

    # Half-repaired forms: first part became ’ but second part remains mojibake.
    "U.S.’揅hina": "U.S.–China",
    "U.S.’揑srael": "U.S.–Israel",
    "Israel’揑ran": "Israel–Iran",

    "China’揅entral": "China–Central",
    "Russia’揅aspian": "Russia–Caspian",
    "Kazakhstan’揅aspian": "Kazakhstan–Caspian",
    "Asia’揅aspian": "Asia–Caspian",
    "Caspian’揑ran": "Caspian–Iran",
    "Asia’揑ran": "Asia–Iran",
    "Sea’揑ran": "Sea–Iran",
    "Pakistan’揑ran": "Pakistan–Iran",
    "Turkmenistan’揑ran": "Turkmenistan–Iran",
    "Asia’揟urkmenistan": "Asia–Turkmenistan",
    "China’揚akistan": "China–Pakistan",
    "China’揥akhan": "China–Wakhan",
    "Wakhan’揂fghanistan": "Wakhan–Afghanistan",
    "Iran’揘orthern": "Iran–Northern",
    "January’揗arch": "January–March",

    # Specific broken policy brief number forms
    "EPINOVA”026’揚B”9": "EPINOVA–2026–PB–49",
    "EPINOVA”026’揚B": "EPINOVA–2026–PB",
    "EPINOVA’揚B": "EPINOVA–PB",

    # Common symbols
    "漏": "©",
    "庐": "®",
    "茅": "é",

    # Known Chinese title mojibake found earlier
    "缇庝紒涓氬瀵逛腑鍥界粡娴庡厖婊℃湡寰?甯屾湜鍔犲己瀵瑰崕鍚堜綔": "美企业家对中国经济充满期待 希望加强对华合作",
}


SUSPICIOUS_MARKERS = [
    "鈥", "檚", "檛", "揅", "揑", "揘", "揗", "揚",
    "揟", "揥", "揂", "漏", "庐", "缇庝", "涓", "鍥", "庝"
]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def repair_text(text: str) -> str:
    new = text

    # ftfy handles many standard mojibake cases safely.
    if fix_text is not None:
        new = fix_text(new)

    # Apply repo-specific repairs repeatedly because some fixes expose later patterns.
    changed = True
    while changed:
        changed = False
        for bad, good in REPLACEMENTS.items():
            if bad in new:
                new = new.replace(bad, good)
                changed = True

    return new


def validate_json_if_needed(path: Path, text: str) -> bool:
    if path.suffix.lower() != ".json":
        return True

    try:
        json.loads(text)
        return True
    except json.JSONDecodeError as exc:
        print(f"SKIP invalid JSON after repair: {path}")
        print(f"  {exc}")
        return False


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    changed_files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if not is_text_file(path):
            continue

        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                original = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                print(f"SKIP non-UTF text: {path}")
                continue

        repaired = repair_text(original)

        if repaired != original:
            if validate_json_if_needed(path, repaired):
                changed_files.append(path)
                if not dry_run:
                    path.write_text(repaired, encoding="utf-8", newline="\n")
                print(("Would fix: " if dry_run else "Fixed: ") + str(path))

    print(f"\nDone. {'Would fix' if dry_run else 'Fixed'} {len(changed_files)} files.")

    print("\nRemaining suspicious markers:")
    remaining = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path) or not is_text_file(path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for marker in SUSPICIOUS_MARKERS:
            if marker in text:
                print(f"  {marker}  ->  {path}")
                remaining += 1
                break

    if remaining == 0:
        print("  None found.")
    else:
        print(f"  {remaining} files still need review.")


if __name__ == "__main__":
    main()