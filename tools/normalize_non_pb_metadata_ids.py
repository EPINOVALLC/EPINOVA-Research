# tools/normalize_non_pb_metadata_ids.py

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


# ============================================================
# Configuration
# ============================================================

SKIP_PATH_KEYWORDS = {
    "article",
    "articles",
    "policy brief",
    "policy briefs",
    "policy-brief",
    "policy-briefs",
}

# These are formal publication types to normalize.
# PB is intentionally excluded.
FORMAL_TYPES = {
    "WP",     # Working Paper
    "IWB",    # Institutional / Index White Book, if used
    "WH",     # White Paper, if used
    "RR",     # Research Report
    "PR",     # Policy Report
    "IMP",    # Index Methodology Paper
}


# ============================================================
# Helpers
# ============================================================

def should_skip_metadata(path: Path) -> bool:
    """
    Skip Articles and Policy Briefs.
    Uses path parts rather than metadata content because your repo
    likely separates categories by folders.
    """
    path_text = " ".join(part.lower() for part in path.parts)

    for keyword in SKIP_PATH_KEYWORDS:
        if keyword in path_text:
            return True

    return False


def pad_number(num: str) -> str:
    """
    Convert 1, 01, 001 into 001 format.
    """
    return f"{int(num):03d}"


def normalize_identifier_text(text: str) -> str:
    """
    Normalize only EPINOVA publication identifiers.
    Do NOT normalize general punctuation, title dashes, page ranges,
    date ranges, prose-level en dashes, or URL casing.
    """

    D = r"[-–—−‒]"

    # ------------------------------------------------------------
    # 0. URL slugs: keep lowercase, only pad final number.
    # ------------------------------------------------------------
    def repl_url_slug(match: re.Match) -> str:
        prefix = match.group(1).lower()
        number = match.group(2)
        suffix = match.group(3)
        return f"{prefix}{pad_number(number)}{suffix}"

    text = re.sub(
        r"(https://publications\.epinova\.org/epinova-(?:wp-[a-z]-|wp-|iwb-|wh-|rr-|pr-|imp-)[0-9]{4}-)([0-9]{1,3})(/)",
        repl_url_slug,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 1. Working Papers with category.
    # Do not match inside URLs: (?<!/)
    # ------------------------------------------------------------
    def repl_wp_category(match: re.Match) -> str:
        category = match.group(1).upper()
        year = match.group(2)
        number = match.group(3)
        return f"EPINOVA-WP-{category}-{year}-{pad_number(number)}"

    text = re.sub(
        rf"(?<!/)\bEPINOVA{D}WP{D}([A-Z]){D}([0-9]{{4}}){D}([0-9]{{1,3}})\b",
        repl_wp_category,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 2. Standard formal types.
    # ------------------------------------------------------------
    def repl_standard_type(match: re.Match) -> str:
        pub_type = match.group(1).upper()
        year = match.group(2)
        number = match.group(3)
        return f"EPINOVA-{pub_type}-{year}-{pad_number(number)}"

    text = re.sub(
        rf"(?<!/)\bEPINOVA{D}(WP|IWB|WH|RR|PR|IMP){D}([0-9]{{4}}){D}([0-9]{{1,3}})\b",
        repl_standard_type,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 3. Old format:
    # EPINOVA-2025-01-RR -> EPINOVA-RR-2025-001
    # ------------------------------------------------------------
    def repl_old_year_number_type(match: re.Match) -> str:
        year = match.group(1)
        number = match.group(2)
        pub_type = match.group(3).upper()
        return f"EPINOVA-{pub_type}-{year}-{pad_number(number)}"

    text = re.sub(
        rf"(?<!/)\bEPINOVA{D}([0-9]{{4}}){D}([0-9]{{1,3}}){D}(RR|PR|WH|IWB|IMP)\b",
        repl_old_year_number_type,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 4. Old variant:
    # EPINOVA-2025-PR-01 -> EPINOVA-PR-2025-001
    # ------------------------------------------------------------
    def repl_old_year_type_number(match: re.Match) -> str:
        year = match.group(1)
        pub_type = match.group(2).upper()
        number = match.group(3)
        return f"EPINOVA-{pub_type}-{year}-{pad_number(number)}"

    text = re.sub(
        rf"(?<!/)\bEPINOVA{D}([0-9]{{4}}){D}(RR|PR|WH|IWB|IMP){D}([0-9]{{1,3}})\b",
        repl_old_year_type_number,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 5. Legacy IWP style.
    # IWP-25-01 / IWP–25–01 -> EPINOVA-IMP-2025-001
    # ------------------------------------------------------------
    def repl_legacy_iwp(match: re.Match) -> str:
        short_year = int(match.group(1))
        number = match.group(2)
        year = 2000 + short_year
        return f"EPINOVA-IMP-{year}-{pad_number(number)}"

    text = re.sub(
        rf"\bIWP{D}([0-9]{{2}}){D}([0-9]{{1,3}})\b",
        repl_legacy_iwp,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------
    # 6. Legacy IWB style.
    # IWB-26-01 / IWB–26–01 -> EPINOVA-IWB-2026-001
    # ------------------------------------------------------------
    def repl_legacy_iwb(match: re.Match) -> str:
        short_year = int(match.group(1))
        number = match.group(2)
        year = 2000 + short_year
        return f"EPINOVA-IWB-{year}-{pad_number(number)}"

    text = re.sub(
        rf"\bIWB{D}([0-9]{{2}}){D}([0-9]{{1,3}})\b",
        repl_legacy_iwb,
        text,
        flags=re.IGNORECASE,
    )

    return text


def normalize_json_obj(obj: Any) -> tuple[Any, list[tuple[str, str]]]:
    """
    Recursively normalize every string field in metadata.json.
    Returns updated object and list of changes.
    """
    changes: list[tuple[str, str]] = []

    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            new_value, sub_changes = normalize_json_obj(value)
            new_obj[key] = new_value
            changes.extend(sub_changes)
        return new_obj, changes

    if isinstance(obj, list):
        new_list = []
        for item in obj:
            new_item, sub_changes = normalize_json_obj(item)
            new_list.append(new_item)
            changes.extend(sub_changes)
        return new_list, changes

    if isinstance(obj, str):
        new_text = normalize_identifier_text(obj)
        if new_text != obj:
            changes.append((obj, new_text))
        return new_text, changes

    return obj, changes


def process_metadata_file(path: Path, apply: bool) -> int:
    """
    Process one metadata.json file.
    Returns number of changes.
    """
    if should_skip_metadata(path):
        return 0

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        print(f"[ERROR] Cannot read JSON: {path}")
        print(f"        {exc}")
        return 0

    new_data, changes = normalize_json_obj(data)

    if not changes:
        return 0

    print("\n" + "=" * 80)
    print(f"[FOUND] {path}")
    print("-" * 80)

    for old, new in changes:
        print(f"OLD: {old}")
        print(f"NEW: {new}")
        print()

    if apply:
        backup_path = path.with_suffix(path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)

        path.write_text(
            json.dumps(new_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"[UPDATED] {path}")
        print(f"[BACKUP ] {backup_path}")
    else:
        print("[DRY-RUN] No file changed. Use --apply to write changes.")

    return len(changes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize non-PB EPINOVA metadata identifiers to three-digit numbering."
    )

    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root. Default: current directory.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes. Without this flag, the script only previews changes.",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Root path does not exist: {root}")

    metadata_files = sorted(root.rglob("metadata.json"))

    print(f"[INFO] Root: {root}")
    print(f"[INFO] Found metadata.json files: {len(metadata_files)}")
    print(f"[INFO] Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    total_files_changed = 0
    total_changes = 0

    for path in metadata_files:
        change_count = process_metadata_file(path, apply=args.apply)
        if change_count > 0:
            total_files_changed += 1
            total_changes += change_count

    print("\n" + "=" * 80)
    print("[SUMMARY]")
    print(f"Files with changes: {total_files_changed}")
    print(f"Total string replacements: {total_changes}")

    if not args.apply:
        print("\nNo files were modified. Run again with --apply after checking the output.")


if __name__ == "__main__":
    main()