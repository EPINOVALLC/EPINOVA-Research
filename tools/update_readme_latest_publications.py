import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote


# =========================================================
# EPINOVA README Full Auto-Updater
#
# Functions:
# - Run git ls-files and generate repository_files.txt
# - Read repository file structure
# - Group publications by category
# - Select latest 5 publications per category
# - Generate GitHub folder/file links
# - Auto-update README.md:
#   1) Overview wording
#   2) Repository Structure section
#   3) Publication Type Codes section
#   4) Latest Publications section
#
# Run from repository root:
# python tools/update_readme_latest_publications.py
# =========================================================

REPO_OWNER = "EPINOVALLC"
REPO_NAME = "EPINOVA-Research"
BRANCH = "main"

README_NAME = "README.md"
REPOSITORY_FILES_NAME = "repository_files.txt"

REPOSITORY_STRUCTURE_TITLE = "## Repository Structure"
PUBLICATION_TYPE_CODES_TITLE = "## Publication Type Codes"
LATEST_SECTION_TITLE = "## Latest Publications"

# These names must match the physical top-level folders in the repository.
CATEGORY_ORDER = [
    "Index Methodology Paper",
    "White Paper",
    "Policy Brief",
    "Policy Report",
    "Research Report",
    "Working Paper",
]

CATEGORY_LABELS = {
    "Index Methodology Paper": "Index Methodology Papers",
    "White Paper": "White Papers",
    "Policy Brief": "Policy Briefs",
    "Policy Report": "Policy Reports",
    "Research Report": "Research Reports",
    "Working Paper": "Working Papers",
}

CATEGORY_CODES = {
    "Index Methodology Paper": "IMP",
    "White Paper": "WHT",
    "Policy Brief": "PB",
    "Policy Report": "PR",
    "Research Report": "RR",
    "Working Paper": "WP",
}

CATEGORY_DESCRIPTIONS = {
    "Index Methodology Paper": (
        "Index construction, measurement frameworks, indicator architecture, normalization, "
        "weighting, classification, validation, and scoring systems."
    ),
    "White Paper": (
        "Institutional white papers presenting conceptual frameworks, policy architectures, "
        "strategic research, and official EPINOVA framework documents."
    ),
    "Policy Brief": (
        "Concise policy analysis, strategic assessment, crisis interpretation, and actionable recommendations."
    ),
    "Policy Report": (
        "Policy-facing reports with more detailed background, evidence, and institutional implications."
    ),
    "Research Report": (
        "Full research reports, case studies, empirical analysis, and extended analytical outputs."
    ),
    "Working Paper": (
        "Academic drafts, theoretical exploration, pre-publication research, and developing arguments."
    ),
}

CATEGORY_PREFIXES = tuple(f"{category}/" for category in CATEGORY_ORDER)

# Optional support directories to show in Repository Structure if they exist.
SUPPORT_DIRS = [
    "Articles",
    "assets",
    "doc",
    "docs",
    "tools",
]


def find_repo_root() -> Path:
    """
    Find repository root by locating .git.
    """
    current = Path(".").resolve()

    for path in [current] + list(current.parents):
        if (path / ".git").exists():
            return path

    return current


ROOT = find_repo_root()
README_PATH = ROOT / README_NAME
REPOSITORY_FILES_PATH = ROOT / REPOSITORY_FILES_NAME


def run_git_ls_files() -> list[str]:
    """
    Run git ls-files and write repository_files.txt.

    Includes tracked, staged, and untracked non-ignored files.
    Uses core.quotePath=false so non-ASCII paths are returned as UTF-8.
    """
    result = subprocess.run(
        [
            "git",
            "-c", "core.quotePath=false",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    paths = [line.strip().strip('"').replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]

    REPOSITORY_FILES_PATH.write_text(
        "\n".join(paths) + "\n",
        encoding="utf-8",
    )

    print(f"Updated: {REPOSITORY_FILES_PATH}")
    print(f"Tracked, staged, and untracked non-ignored files: {len(paths)}")

    return paths


def github_blob_url(relative_path: str) -> str:
    return (
        f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/"
        f"{BRANCH}/{quote(relative_path, safe='/')}"
    )


def github_tree_url(relative_folder: str) -> str:
    return (
        f"https://github.com/{REPO_OWNER}/{REPO_NAME}/tree/"
        f"{BRANCH}/{quote(relative_folder, safe='/')}"
    )


def is_source_publication_pdf(path: str) -> bool:
    """
    Keep only source publication PDFs under the main publication categories.
    Exclude generated docs/ PDFs.
    """
    normalized = path.replace("\\", "/")

    if not normalized.lower().endswith(".pdf"):
        return False

    if normalized.startswith("docs/"):
        return False

    return normalized.startswith(CATEGORY_PREFIXES)


def get_category(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    for category in CATEGORY_ORDER:
        if normalized.startswith(f"{category}/"):
            return category
    return None


def read_metadata(folder: Path) -> dict:
    """
    Read metadata.json or metadat.json if present.
    """
    candidates = [
        folder / "metadata.json",
        folder / "metadat.json",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"Warning: failed to read metadata: {candidate} ({exc})")
                return {}

    return {}


def clean_pdf_title(filename: str) -> str:
    title = filename
    if title.lower().endswith(".pdf"):
        title = title[:-4]

    title = title.replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip()

    return title


def full_title_from_metadata(metadata: dict, fallback_title: str) -> str:
    title = (
        metadata.get("full_title")
        or metadata.get("title_full")
        or metadata.get("publication_title")
        or metadata.get("title")
        or fallback_title
    )

    subtitle = metadata.get("subtitle", "")
    if subtitle and subtitle not in str(title):
        return f"{title}: {subtitle}"

    return str(title).strip()


def extract_year(path: str) -> str:
    match = re.search(r"(20\d{2})", path)
    return match.group(1) if match else ""


def extract_date(path: str) -> str:
    """
    Extract YYYY-MM-DD if present.
    """
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", path)
    return match.group(1) if match else ""


def extract_numeric_rank(text: str) -> int:
    """
    Extract the last number from folder or identifier for sorting.
    """
    nums = re.findall(r"\d+", text)
    if not nums:
        return -1
    return int(nums[-1])


def publication_record(pdf_path: str) -> dict:
    pdf = ROOT / pdf_path
    folder = pdf.parent
    folder_rel = str(folder.relative_to(ROOT)).replace("\\", "/")

    metadata = read_metadata(folder)
    fallback_title = clean_pdf_title(pdf.name)

    title = full_title_from_metadata(metadata, fallback_title)

    epinova_id = (
        metadata.get("epinova_id")
        or metadata.get("identifier")
        or folder.name
    )

    publication_date = (
        metadata.get("publication_date")
        or metadata.get("date")
        or extract_date(pdf_path)
        or extract_year(pdf_path)
    )

    category = get_category(pdf_path)

    return {
        "category": category,
        "category_label": CATEGORY_LABELS.get(category, category),
        "title": str(title).strip(),
        "epinova_id": str(epinova_id).strip(),
        "publication_date": str(publication_date).strip(),
        "folder": folder_rel,
        "filename": pdf.name,
        "pdf_path": pdf_path.replace("\\", "/"),
        "rank_number": extract_numeric_rank(str(epinova_id) + " " + folder.name),
        "year": extract_year(pdf_path),
    }


def sort_key(record: dict):
    """
    Sort latest first.
    Prefer year and identifier number, then publication_date.
    This avoids one incorrect metadata date pushing an older record upward.
    """
    return (
        record.get("year", ""),
        record.get("rank_number", -1),
        record.get("publication_date", ""),
        record.get("title", ""),
    )


def detect_top_level_dirs(paths: list[str]) -> set[str]:
    dirs = set()
    for path in paths:
        normalized = path.replace("\\", "/")
        if "/" in normalized:
            dirs.add(normalized.split("/", 1)[0])
    return dirs


def build_repository_structure_section(paths: list[str]) -> str:
    """
    Build README Repository Structure from actual repository folders.
    """
    existing_top_dirs = detect_top_level_dirs(paths)

    ordered_dirs = []

    # Put Articles first if present, then publication categories.
    if "Articles" in existing_top_dirs or (ROOT / "Articles").exists():
        ordered_dirs.append("Articles")

    for dirname in CATEGORY_ORDER:
        if dirname in existing_top_dirs or (ROOT / dirname).exists():
            ordered_dirs.append(dirname)

    for dirname in SUPPORT_DIRS:
        if dirname not in ordered_dirs and (dirname in existing_top_dirs or (ROOT / dirname).exists()):
            ordered_dirs.append(dirname)

    if not ordered_dirs:
        ordered_dirs = CATEGORY_ORDER + ["assets", "docs", "tools"]

    tree_lines = ["EPINOVA-Research/"]
    for index, dirname in enumerate(ordered_dirs):
        connector = "└──" if index == len(ordered_dirs) - 1 else "├──"
        tree_lines.append(f"{connector} {dirname}/")

    body = [
        REPOSITORY_STRUCTURE_TITLE,
        "",
        "```text",
        *tree_lines,
        "```",
        "",
        "Each publication folder typically contains:",
        "",
        "```text",
        "publication.pdf",
        "metadata.json",
        "```",
        "",
        "The `Index Methodology Paper/` directory is used for index-construction and measurement-framework publications, including indicator architecture, normalization, weighting, classification, validation, and scoring methodology.",
        "",
        "The `White Paper/` directory is used for broader institutional white papers, conceptual frameworks, policy architectures, and strategic framework documents.",
        "",
        "The `docs/` directory contains the generated static publication site deployed through Cloudflare Pages.",
        "",
    ]

    return "\n".join(body).rstrip() + "\n"


def build_publication_type_codes_section() -> str:
    """
    Build README Publication Type Codes section.
    """
    lines = [
        PUBLICATION_TYPE_CODES_TITLE,
        "",
        "| Publication Type | Code | Use |",
        "|---|---:|---|",
    ]

    for category in CATEGORY_ORDER:
        lines.append(
            f"| {category} | {CATEGORY_CODES[category]} | {CATEGORY_DESCRIPTIONS[category]} |"
        )

    lines.extend([
        "",
        "Notes:",
        "",
        "- `WP` is reserved for Working Paper.",
        "- `WHT` is used for White Paper. The code is derived from “White” to avoid conflict with `WP`.",
        "- `IMP` is used for Index Methodology Paper, especially documents focused on how an index is constructed, measured, weighted, validated, and applied.",
        "- For index projects, use `IMP` when the document is primarily methodological, and use `WHT` when the document is broader, more policy-facing, or intended as an institutional white paper.",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


def build_latest_publications_section(records: list[dict], limit_per_category: int = 5) -> str:
    grouped = {category: [] for category in CATEGORY_ORDER}

    for record in records:
        category = record.get("category")
        if category in grouped:
            grouped[category].append(record)

    lines = [
        LATEST_SECTION_TITLE,
        "",
        "The links below point to the current GitHub repository structure. "
        "Folder names are preserved as they currently exist in the repository to avoid broken links.",
        "",
        "### DOI Status Notice",
        "",
        "Zenodo is currently not used as the primary publication access layer for this repository. "
        "Some previous EPINOVA records may have Zenodo archival identifiers, but the current repository "
        "and publication workflow is organized around GitHub source folders, EPINOVA publication landing pages, "
        "and pending Crossref DOI registration.",
        "",
        "Until Crossref membership approval and DOI prefix assignment are completed, newly prepared EPINOVA "
        "publication records should use the following DOI status statement:",
        "",
        "```text",
        "DOI: To be assigned after Crossref membership approval.",
        "```",
        "",
        "After Crossref registration is completed, DOI fields and citation records will be updated accordingly.",
        "",
    ]

    for category in CATEGORY_ORDER:
        items = sorted(grouped[category], key=sort_key, reverse=True)[:limit_per_category]
        if not items:
            continue

        label = CATEGORY_LABELS[category]
        lines.append(f"### {label}")
        lines.append("")

        for item in items:
            date_text = f" ({item['publication_date']})" if item.get("publication_date") else ""

            lines.extend([
                f"- **{item['epinova_id']}**{date_text}  ",
                f"  **{item['title']}**  ",
                f"  Repository folder: [`{item['folder']}/`]({github_tree_url(item['folder'])})  ",
                f"  File: [`{item['filename']}`]({github_blob_url(item['pdf_path'])})",
                "",
            ])

        lines.append("---")
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    if lines and lines[-1] == "---":
        lines.pop()

    return "\n".join(lines).rstrip() + "\n"


def replace_level2_section(readme_text: str, heading: str, new_section: str, insert_before_heading: str | None = None) -> str:
    """
    Replace a Markdown level-2 section from heading to the next level-2 heading.
    If the section does not exist, insert it before insert_before_heading if found; otherwise append it.
    """
    escaped_heading = re.escape(heading)
    pattern = re.compile(
        rf"{escaped_heading}(?:\s*\n).*?(?=\n## |\Z)",
        re.DOTALL,
    )

    if pattern.search(readme_text):
        return pattern.sub(new_section.rstrip(), readme_text)

    if insert_before_heading:
        marker = f"\n{insert_before_heading}"
        if marker in readme_text:
            return readme_text.replace(
                marker,
                "\n" + new_section.rstrip() + "\n" + marker,
                1,
            )

    return readme_text.rstrip() + "\n\n" + new_section.rstrip() + "\n"


def replace_latest_section(readme_text: str, latest_section: str) -> str:
    """
    Replace from ## Latest Publications or old ## Latest Publications and Repository Links
    to the next ## heading.
    """
    pattern = re.compile(
        r"## Latest Publications(?: and Repository Links)?\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )

    if pattern.search(readme_text):
        return pattern.sub(latest_section.rstrip(), readme_text)

    insert_heading = "\n## Publication Metadata"
    if insert_heading in readme_text:
        return readme_text.replace(
            insert_heading,
            "\n" + latest_section.rstrip() + "\n" + insert_heading,
            1,
        )

    return readme_text.rstrip() + "\n\n" + latest_section.rstrip() + "\n"


def update_overview_text(readme_text: str) -> str:
    """
    Update common old wording without rewriting the full Overview.
    """
    replacements = {
        "- conceptual frameworks and white papers;": "- conceptual frameworks, white papers, and index methodology papers;",
        "- conceptual frameworks, white papers;": "- conceptual frameworks, white papers, and index methodology papers;",
        "Index White Paper": "Index Methodology Paper",
        "Index White Papers": "Index Methodology Papers",
        "Index White Book": "Index Methodology Paper",
        "Index White Books": "Index Methodology Papers",
    }

    updated = readme_text
    for old, new in replacements.items():
        updated = updated.replace(old, new)

    return updated


def update_readme(readme_text: str, paths: list[str], records: list[dict]) -> str:
    """
    Apply all README updates.
    """
    updated = update_overview_text(readme_text)

    repository_structure = build_repository_structure_section(paths)
    publication_type_codes = build_publication_type_codes_section()
    latest_publications = build_latest_publications_section(records, limit_per_category=5)

    updated = replace_level2_section(
        updated,
        REPOSITORY_STRUCTURE_TITLE,
        repository_structure,
        insert_before_heading=PUBLICATION_TYPE_CODES_TITLE,
    )

    updated = replace_level2_section(
        updated,
        PUBLICATION_TYPE_CODES_TITLE,
        publication_type_codes,
        insert_before_heading=LATEST_SECTION_TITLE,
    )

    updated = replace_latest_section(updated, latest_publications)

    return updated.rstrip() + "\n"


def print_debug_summary(records: list[dict]) -> None:
    counts = {category: 0 for category in CATEGORY_ORDER}
    for record in records:
        category = record.get("category")
        if category in counts:
            counts[category] += 1

    print("Publication category counts:")
    for category in CATEGORY_ORDER:
        print(f"  - {category}: {counts[category]}")

    imp_records = [
        record for record in records
        if record.get("category") == "Index Methodology Paper"
        or "IMP" in record.get("epinova_id", "")
        or "Index Methodology Paper" in record.get("folder", "")
    ]

    if imp_records:
        print("Index Methodology Paper records detected:")
        for record in imp_records:
            print(f"  - {record.get('epinova_id')} | {record.get('folder')}/ | {record.get('filename')}")
    else:
        print("Index Methodology Paper records detected: 0")


def main() -> None:
    print(f"Repository root: {ROOT}")

    if not README_PATH.exists():
        raise FileNotFoundError(f"README.md not found: {README_PATH}")

    paths = run_git_ls_files()

    pdf_paths = [path for path in paths if is_source_publication_pdf(path)]

    print(f"Source publication PDFs found: {len(pdf_paths)}")

    records = [publication_record(path) for path in pdf_paths]

    print_debug_summary(records)

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_readme = update_readme(readme_text, paths, records)

    README_PATH.write_text(updated_readme, encoding="utf-8")

    print(f"Updated: {README_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
