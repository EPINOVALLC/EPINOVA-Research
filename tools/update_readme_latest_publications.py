import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote


# =========================================================
# EPINOVA README Latest Publications Auto-Updater
#
# Functions:
# - Run git ls-tree and generate repository_files.txt
# - Read repository file structure
# - Group publications by category
# - Select latest 5 publications per category
# - Generate GitHub folder/file links
# - Replace README.md Latest Publications section
#
# Run from repository root:
# python tools/update_readme_latest_publications.py
# =========================================================

REPO_OWNER = "EPINOVALLC"
REPO_NAME = "EPINOVA-Research"
BRANCH = "main"

README_NAME = "README.md"
REPOSITORY_FILES_NAME = "repository_files.txt"

LATEST_SECTION_TITLE = "## Latest Publications"

CATEGORY_ORDER = [
    "Index White Book",
    "Policy Brief",
    "Policy Report",
    "Research Report",
    "Working Paper",
]

CATEGORY_LABELS = {
    "Index White Book": "White Books",
    "Policy Brief": "Policy Briefs",
    "Policy Report": "Policy Reports",
    "Research Report": "Research Reports",
    "Working Paper": "Working Papers",
}

CATEGORY_PREFIXES = tuple(f"{category}/" for category in CATEGORY_ORDER)


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

    paths = [line.strip().strip('"') for line in result.stdout.splitlines() if line.strip()]

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
    if not path.lower().endswith(".pdf"):
        return False

    if path.startswith("docs/"):
        return False

    return path.startswith(CATEGORY_PREFIXES)


def get_category(path: str) -> str | None:
    for category in CATEGORY_ORDER:
        if path.startswith(f"{category}/"):
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

    title = (
        metadata.get("title")
        or metadata.get("publication_title")
        or clean_pdf_title(pdf.name)
    )

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
        "pdf_path": pdf_path,
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

    # Remove final separator for cleaner README.
    while lines and lines[-1] == "":
        lines.pop()

    if lines and lines[-1] == "---":
        lines.pop()

    return "\n".join(lines).rstrip() + "\n"


def replace_latest_section(readme_text: str, latest_section: str) -> str:
    """
    Replace from ## Latest Publications to the next ## heading.
    If missing, insert before ## Publication Metadata, otherwise append.
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


def main() -> None:
    print(f"Repository root: {ROOT}")

    if not README_PATH.exists():
        raise FileNotFoundError(f"README.md not found: {README_PATH}")

    paths = run_git_ls_files()

    pdf_paths = [path for path in paths if is_source_publication_pdf(path)]

    print(f"Source publication PDFs found: {len(pdf_paths)}")

    records = [publication_record(path) for path in pdf_paths]

    latest_section = build_latest_publications_section(
        records,
        limit_per_category=5,
    )

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_readme = replace_latest_section(readme_text, latest_section)

    README_PATH.write_text(updated_readme, encoding="utf-8")

    print(f"Updated: {README_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()