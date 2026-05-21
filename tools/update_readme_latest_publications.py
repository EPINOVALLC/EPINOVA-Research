import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote


# =========================================================
# EPINOVA README Full Auto-Updater
#
# Current publication workflow:
# - EPINOVA publication landing pages are the primary public access layer.
# - Crossref DOI records are the formal DOI registration layer when available.
# - During the Crossref migration period, Zenodo/DataCite DOIs may be displayed
#   as temporary archival DOI links.
# - GitHub source folders/files remain transparency and version-traceability references.
#
# Functions:
# - Run git ls-files and generate repository_files.txt
# - Read repository file structure
# - Group publications by category, including Journal Article records
# - Select latest 5 publications per category
# - Generate publication landing page, DOI, GitHub folder, and source PDF links
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

PUBLICATIONS_SITE_BASE = "https://publications.epinova.org"

README_NAME = "README.md"
REPOSITORY_FILES_NAME = "repository_files.txt"

REPOSITORY_STRUCTURE_TITLE = "## Repository Structure"
PUBLICATION_TYPE_CODES_TITLE = "## Publication Type Codes"
LATEST_SECTION_TITLE = "## Latest Publications"


# These names must match the physical top-level folders in the repository.
CATEGORY_ORDER = [
    "Index Methodology Paper",
    "Journal Article",
    "White Paper",
    "Policy Brief",
    "Policy Report",
    "Research Report",
    "Working Paper",
]


CATEGORY_LABELS = {
    "Index Methodology Paper": "Index Methodology Papers",
    "Journal Article": "Journal Articles",
    "White Paper": "White Papers",
    "Policy Brief": "Policy Briefs",
    "Policy Report": "Policy Reports",
    "Research Report": "Research Reports",
    "Working Paper": "Working Papers",
}


CATEGORY_CODES = {
    "Index Methodology Paper": "IMP",
    "Journal Article": "JA",
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
    "Journal Article": (
        "Externally published or journal-style articles, including author-archived versions, "
        "publication records, magazine articles, and scholarly articles published outside the EPINOVA report series."
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


# Metadata field aliases.
TITLE_FIELDS = [
    "full_title",
    "title_full",
    "publication_title",
    "title",
]


SUBTITLE_FIELDS = [
    "subtitle",
    "sub_title",
]


IDENTIFIER_FIELDS = [
    "record_id",
    "epinova_id",
    "publication_id",
    "identifier",
    "id",
]


DATE_FIELDS = [
    "publication_date",
    "date",
    "issued",
    "published_date",
]


LANDING_PAGE_FIELDS = [
    "official_page",
    "publication_url",
    "landing_page",
    "canonical_url",
    "url",
    "html_url",
]


DOI_FIELDS = [
    "doi",
    "crossref_doi",
    "crossref",
]


LEGACY_DOI_FIELDS = [
    "zenodo_doi",
    "datacite_doi",
    "legacy_doi",
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
            "-c",
            "core.quotePath=false",
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

    paths = [
        line.strip().strip('"').replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    ]

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


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def normalize_doi(value: str | None) -> str:
    """
    Normalize DOI values.

    Accepts:
    - 10.xxxx/xxxx
    - https://doi.org/10.xxxx/xxxx
    - http://doi.org/10.xxxx/xxxx
    - DOI: 10.xxxx/xxxx
    - doi:10.xxxx/xxxx
    """
    if not value:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    text = text.replace("DOI:", "").replace("doi:", "").strip()

    if text.startswith("https://doi.org/"):
        text = text.replace("https://doi.org/", "", 1).strip()

    if text.startswith("http://doi.org/"):
        text = text.replace("http://doi.org/", "", 1).strip()

    return text


def doi_url(doi: str) -> str:
    normalized = normalize_doi(doi)
    return f"https://doi.org/{normalized}" if normalized else ""


def first_metadata_value(metadata: dict, fields: list[str]) -> str:
    """
    Return the first non-empty metadata value from a list of possible field names.
    """
    for field in fields:
        value = metadata.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def is_zenodo_or_datacite_doi(doi: str) -> bool:
    """
    EPINOVA previously used Zenodo/DataCite DOIs, usually 10.5281/zenodo...
    These may be displayed temporarily as archival DOI links during Crossref migration.
    """
    normalized = normalize_doi(doi).lower()
    return normalized.startswith("10.5281/zenodo")


def is_crossref_like_doi(doi: str) -> bool:
    """
    Treat non-Zenodo DOI as current DOI candidate.
    For EPINOVA Crossref records, this will normally include the Crossref prefix.
    """
    normalized = normalize_doi(doi)
    if not normalized:
        return False
    if is_zenodo_or_datacite_doi(normalized):
        return False
    return normalized.startswith("10.")


def is_source_publication_pdf(path: str) -> bool:
    """
    Keep only source publication PDFs under the main publication categories.
    Exclude generated docs/ PDFs.
    """
    normalized = normalize_path(path)

    if not normalized.lower().endswith(".pdf"):
        return False

    if normalized.startswith("docs/"):
        return False

    return normalized.startswith(CATEGORY_PREFIXES)


def get_category(path: str) -> str | None:
    normalized = normalize_path(path)
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
    title = first_metadata_value(metadata, TITLE_FIELDS) or fallback_title
    subtitle = first_metadata_value(metadata, SUBTITLE_FIELDS)

    title = str(title).strip()
    subtitle = str(subtitle).strip()

    if subtitle and subtitle not in title:
        return f"{title}: {subtitle}"

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


def normalize_url(value: str | None) -> str:
    if not value:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if text.startswith("http://") or text.startswith("https://"):
        return text

    if text.startswith("/"):
        return PUBLICATIONS_SITE_BASE.rstrip("/") + text

    return text


def publication_page_from_metadata(metadata: dict) -> str:
    return normalize_url(first_metadata_value(metadata, LANDING_PAGE_FIELDS))


def current_doi_from_metadata(metadata: dict) -> str:
    """
    Prefer Crossref/current DOI fields.
    If only a DOI field exists but it is a Zenodo/DataCite DOI, do not treat it
    as the current DOI.
    """
    for field in DOI_FIELDS:
        raw_value = metadata.get(field)
        if raw_value is None:
            continue

        normalized = normalize_doi(str(raw_value))
        if is_crossref_like_doi(normalized):
            return normalized

    return ""


def legacy_doi_from_metadata(metadata: dict) -> str:
    """
    Capture Zenodo/DataCite/legacy DOI if present.

    This function also checks the normal DOI fields because older records may store
    Zenodo DOI directly under "doi".
    """
    for field in LEGACY_DOI_FIELDS + DOI_FIELDS:
        raw_value = metadata.get(field)
        if raw_value is None:
            continue

        normalized = normalize_doi(str(raw_value))
        if is_zenodo_or_datacite_doi(normalized):
            return normalized

    return ""


def publication_record(pdf_path: str) -> dict:
    pdf = ROOT / pdf_path
    folder = pdf.parent
    folder_rel = str(folder.relative_to(ROOT)).replace("\\", "/")

    metadata = read_metadata(folder)
    fallback_title = clean_pdf_title(pdf.name)

    title = full_title_from_metadata(metadata, fallback_title)

    epinova_id = (
        first_metadata_value(metadata, IDENTIFIER_FIELDS)
        or folder.name
    )

    publication_date = (
        first_metadata_value(metadata, DATE_FIELDS)
        or extract_date(pdf_path)
        or extract_year(pdf_path)
    )

    category = get_category(pdf_path)

    current_doi = current_doi_from_metadata(metadata)
    legacy_doi = legacy_doi_from_metadata(metadata)
    publication_page = publication_page_from_metadata(metadata)

    # Transitional DOI display rule:
    # - Prefer Crossref/current DOI if available.
    # - If not available, temporarily display Zenodo/DataCite DOI.
    # - Mark whether the displayed DOI is current or temporary archival.
    display_doi = current_doi or legacy_doi
    display_doi_status = "current" if current_doi else ("legacy" if legacy_doi else "missing")

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
        "publication_page": publication_page,
        "doi": current_doi,
        "legacy_doi": legacy_doi,
        "display_doi": display_doi,
        "display_doi_status": display_doi_status,
        "metadata": metadata,
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
        normalized = normalize_path(path)
        if "/" in normalized:
            dirs.add(normalized.split("/", 1)[0])
    return dirs


def build_repository_structure_section(paths: list[str]) -> str:
    """
    Build README Repository Structure from actual repository folders.
    """
    existing_top_dirs = detect_top_level_dirs(paths)

    ordered_dirs = []

    if "Articles" in existing_top_dirs or (ROOT / "Articles").exists():
        ordered_dirs.append("Articles")

    for dirname in CATEGORY_ORDER:
        if dirname in existing_top_dirs or (ROOT / dirname).exists():
            ordered_dirs.append(dirname)

    for dirname in SUPPORT_DIRS:
        if dirname not in ordered_dirs and (
            dirname in existing_top_dirs or (ROOT / dirname).exists()
        ):
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
        "Each publication source folder typically contains:",
        "",
        "```text",
        "publication.pdf",
        "metadata.json",
        "```",
        "",
        "The repository is the source and version-traceability layer for EPINOVA publications. "
        "The primary public access layer is the EPINOVA publication landing-page system, while DOI metadata is registered through Crossref when available.",
        "",
        "The `Index Methodology Paper/` directory is used for index-construction and measurement-framework publications, including indicator architecture, normalization, weighting, classification, validation, and scoring methodology.",
        "",
        "The `Journal Article/` directory is used for externally published or journal-style articles, including author-archived versions, publication records, magazine articles, and scholarly articles published outside the EPINOVA report series.",
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

    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- `WP` is reserved for Working Paper.",
            "- `WHT` is used for White Paper. The code is derived from “White” to avoid conflict with `WP`.",
            "- `IMP` is used for Index Methodology Paper, especially documents focused on how an index is constructed, measured, weighted, validated, and applied.",
            "- `JA` is used for Journal Article, especially externally published articles or author-archived article records that should not be mixed into EPINOVA policy brief/report numbering.",
            "- For index projects, use `IMP` when the document is primarily methodological, and use `WHT` when the document is broader, more policy-facing, or intended as an institutional white paper.",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def markdown_link(label: str, url: str) -> str:
    if not url:
        return ""
    return f"[{label}]({url})"


def build_publication_item_lines(item: dict) -> list[str]:
    date_text = f" ({item['publication_date']})" if item.get("publication_date") else ""

    publication_page = item.get("publication_page", "")
    display_doi = item.get("display_doi", "")
    display_doi_status = item.get("display_doi_status", "missing")

    lines = [
        f"- **{item['epinova_id']}**{date_text}  ",
        f"  **{item['title']}**  ",
    ]

    if publication_page:
        lines.append(
            f"  Publication page: {markdown_link(publication_page, publication_page)}  "
        )
    else:
        lines.append(
            "  Publication page: Not listed in metadata.  "
        )

    if display_doi:
        if display_doi_status == "current":
            lines.append(
                f"  DOI: {markdown_link(display_doi, doi_url(display_doi))}  "
            )
        else:
            lines.append(
                f"  Temporary archival DOI: {markdown_link(display_doi, doi_url(display_doi))}  "
            )
    else:
        lines.append(
            "  DOI: To be assigned or updated after Crossref registration.  "
        )

    lines.extend(
        [
            f"  Source folder: [`{item['folder']}/`]({github_tree_url(item['folder'])})  ",
            f"  Source PDF: [`{item['filename']}`]({github_blob_url(item['pdf_path'])})",
            "",
        ]
    )

    return lines


def build_latest_publications_section(records: list[dict], limit_per_category: int = 5) -> str:
    grouped = {category: [] for category in CATEGORY_ORDER}

    for record in records:
        category = record.get("category")
        if category in grouped:
            grouped[category].append(record)

    lines = [
        LATEST_SECTION_TITLE,
        "",
        "The links below prioritize EPINOVA publication landing pages where available. "
        "GitHub links are retained as source-folder and source-file references for transparency, preservation, and version traceability.",
        "",
        "### DOI and Access Notice",
        "",
        "EPINOVA publication landing pages serve as the primary public access layer for current publication records. "
        "Crossref DOI records are used as the formal DOI registration layer when available.",
        "",
        "During the Crossref migration period, existing Zenodo/DataCite DOI records may be displayed as temporary archival DOI links. "
        "These identifiers are retained for continuity, citation traceability, and archival access, but they may later be superseded by Crossref DOI records.",
        "",
        "For newly prepared records that have not yet completed Crossref registration and do not have a temporary archival DOI, use the following temporary status statement:",
        "",
        "```text",
        "DOI: Temporary archival DOI shown when available; otherwise to be assigned or updated after Crossref registration.",
        "```",
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
            lines.extend(build_publication_item_lines(item))

        lines.append("---")
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    if lines and lines[-1] == "---":
        lines.pop()

    return "\n".join(lines).rstrip() + "\n"


def replace_level2_section(
    readme_text: str,
    heading: str,
    new_section: str,
    insert_before_heading: str | None = None,
) -> str:
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
        "- conceptual frameworks and white papers;": "- conceptual frameworks, white papers, journal articles, and index methodology papers;",
        "- conceptual frameworks, white papers;": "- conceptual frameworks, white papers, journal articles, and index methodology papers;",
        "- conceptual frameworks, white papers, and index methodology papers;": "- conceptual frameworks, white papers, journal articles, and index methodology papers;",
        "Index White Paper": "Index Methodology Paper",
        "Index White Papers": "Index Methodology Papers",
        "Index White Book": "Index Methodology Paper",
        "Index White Books": "Index Methodology Papers",
        "Zenodo is currently not used as the primary publication access layer": "Zenodo/DataCite records may be displayed as temporary archival DOI links during Crossref migration",
        "pending Crossref DOI registration": "Crossref DOI registration when available",
        "pending Crossref membership approval": "Crossref registration",
        "DOI: To be assigned after Crossref membership approval.": "DOI: Temporary archival DOI shown when available; otherwise to be assigned or updated after Crossref registration.",
        "DOI: To be assigned or updated after Crossref registration.": "DOI: Temporary archival DOI shown when available; otherwise to be assigned or updated after Crossref registration.",
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
    landing_count = 0
    current_doi_count = 0
    legacy_doi_count = 0
    display_doi_count = 0

    for record in records:
        category = record.get("category")
        if category in counts:
            counts[category] += 1

        if record.get("publication_page"):
            landing_count += 1

        if record.get("doi"):
            current_doi_count += 1

        if record.get("legacy_doi"):
            legacy_doi_count += 1

        if record.get("display_doi"):
            display_doi_count += 1

    print("Publication category counts:")
    for category in CATEGORY_ORDER:
        print(f"  - {category}: {counts[category]}")

    print("Publication metadata coverage:")
    print(f"  - Publication landing pages detected: {landing_count}")
    print(f"  - Current/Crossref DOI values detected: {current_doi_count}")
    print(f"  - Temporary Zenodo/DataCite archival DOI values detected: {legacy_doi_count}")
    print(f"  - Displayable DOI values detected: {display_doi_count}")

    imp_records = [
        record
        for record in records
        if record.get("category") == "Index Methodology Paper"
        or "IMP" in record.get("epinova_id", "")
        or "Index Methodology Paper" in record.get("folder", "")
    ]

    if imp_records:
        print("Index Methodology Paper records detected:")
        for record in imp_records:
            print(
                f"  - {record.get('epinova_id')} | "
                f"{record.get('folder')}/ | "
                f"{record.get('filename')}"
            )
    else:
        print("Index Methodology Paper records detected: 0")


def print_missing_metadata_warnings(records: list[dict]) -> None:
    """
    Print compact metadata warnings without flooding the terminal.

    Transitional rule:
    - Publication landing page is expected.
    - Crossref DOI is not mandatory during the migration period.
    - Zenodo/DataCite DOI can temporarily serve as displayed archival DOI.
    """
    missing_page = [
        record for record in records
        if not record.get("publication_page")
    ]

    has_current_doi = [
        record for record in records
        if record.get("doi")
    ]

    has_legacy_doi_only = [
        record for record in records
        if not record.get("doi") and record.get("legacy_doi")
    ]

    has_no_doi = [
        record for record in records
        if not record.get("doi") and not record.get("legacy_doi")
    ]

    if missing_page:
        print("Warning: records without publication landing page in metadata:")
        for record in sorted(missing_page, key=sort_key, reverse=True)[:20]:
            print(f"  - {record.get('epinova_id')} | {record.get('folder')}/")

        if len(missing_page) > 20:
            print(f"  ... plus {len(missing_page) - 20} more")

    print("DOI transition summary:")
    print(f"  - Records with current/Crossref DOI: {len(has_current_doi)}")
    print(f"  - Records using temporary Zenodo/DataCite archival DOI: {len(has_legacy_doi_only)}")
    print(f"  - Records with no DOI available yet: {len(has_no_doi)}")

    if has_no_doi:
        print("Notice: records with neither current DOI nor temporary archival DOI:")
        for record in sorted(has_no_doi, key=sort_key, reverse=True)[:20]:
            print(f"  - {record.get('epinova_id')} | {record.get('folder')}/")

        if len(has_no_doi) > 20:
            print(f"  ... plus {len(has_no_doi) - 20} more")


def main() -> None:
    print(f"Repository root: {ROOT}")

    if not README_PATH.exists():
        raise FileNotFoundError(f"README.md not found: {README_PATH}")

    paths = run_git_ls_files()

    pdf_paths = [path for path in paths if is_source_publication_pdf(path)]

    print(f"Source publication PDFs found: {len(pdf_paths)}")

    records = [publication_record(path) for path in pdf_paths]

    print_debug_summary(records)
    print_missing_metadata_warnings(records)

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_readme = update_readme(readme_text, paths, records)

    README_PATH.write_text(updated_readme, encoding="utf-8")

    print(f"Updated: {README_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()