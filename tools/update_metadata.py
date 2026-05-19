from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote

# =========================================================
# EPINOVA Metadata Auto-Updater
# For EPINOVA-Research repository
#
# Current-rule version
#
# Safety model:
# - Default mode is DRY-RUN. Use --apply to write files.
# - Does not overwrite existing landing_page unless explicitly empty.
# - Does not overwrite customized metadata_source.notes, especially legacy notes.
# - Preserves DataCite / Zenodo DOI records unless a Crossref DOI is actually present.
# - Normalizes DOI suffixes from epinova_id with a three-digit final number.
# - Keeps URL slugs lowercase.
# - Normalizes Shaoyuan Wu creator metadata while recognizing Shao-Yuan variants.
# =========================================================

REPO_OWNER = "EPINOVALLC"
REPO_NAME = "EPINOVA-Research"
BRANCH = "main"

PUBLICATION_BASE_URL = "https://publications.epinova.org"
METADATA_NAME = "metadata.json"

DOI_PENDING = "To be assigned after Crossref membership approval"
AUTHOR_ORCID = "https://orcid.org/0009-0008-0660-8232"

CROSSREF_PREFIX = "10.67037"

DEFAULT_SKIP_PARTS = {
    ".git",
    "__pycache__",
    "docs",
    "site",
    "generated",
}

# Articles are intentionally not forced into three-digit formal-publication numbering.
# This updater can still process them if --include-articles is supplied.
ARTICLE_PARTS = {"Articles", "articles"}


# =========================================================
# Path helpers
# =========================================================

def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(".")).resolve()

    if current.name == REPO_NAME:
        return current

    candidate = current / REPO_NAME
    if candidate.exists() and candidate.is_dir():
        return candidate.resolve()

    for parent in [current] + list(current.parents):
        if parent.name == REPO_NAME:
            return parent.resolve()

    return current


def encode_path(path: Path) -> str:
    return "/".join(quote(part) for part in path.parts)


def github_blob_url(relative_file: Path) -> str:
    return (
        f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/"
        f"{BRANCH}/{encode_path(relative_file)}"
    )


def github_tree_url(relative_folder: Path) -> str:
    return (
        f"https://github.com/{REPO_OWNER}/{REPO_NAME}/tree/"
        f"{BRANCH}/{encode_path(relative_folder)}"
    )


# ROOT is assigned in main(); functions receive root explicitly where needed.
ROOT = Path(".").resolve()


# =========================================================
# Identifier / DOI / slug helpers
# =========================================================

def normalize_dash_for_identifier(value: str) -> str:
    return (
        (value or "")
        .strip()
        .replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
        .replace("‒", "-")
        .replace("_", "-")
    )


def normalize_slug(value: str) -> str:
    """
    Converts EPINOVA-WP-A-2026-003 into epinova-wp-a-2026-003.
    Keeps publication landing-page slugs lowercase.
    """
    value = normalize_dash_for_identifier(value).lower()
    value = value.replace(" ", "-").replace(".", "-")

    while "--" in value:
        value = value.replace("--", "-")

    return value.strip("-")


def normalize_epinova_id_final_number(epinova_id: str) -> str:
    """
    Returns an EPINOVA identifier with the final numeric component padded to 3 digits.

    Examples:
      EPINOVA-WP-A-2026-03  -> EPINOVA-WP-A-2026-003
      EPINOVA-IMP-2026-01   -> EPINOVA-IMP-2026-001
      EPINOVA-PB-2026-049   -> EPINOVA-PB-2026-049
    """
    cleaned = normalize_dash_for_identifier(epinova_id)
    parts = [p for p in cleaned.split("-") if p]

    if not parts:
        return ""

    if parts[-1].isdigit():
        parts[-1] = parts[-1].zfill(3)

    return "-".join(parts)


def doi_suffix_from_epinova_id(epinova_id: str) -> str:
    """
    Converts:
      EPINOVA-PB-2026-049     -> epinova.pb.2026.049
      EPINOVA-WP-A-2026-003   -> epinova.wp.a.2026.003
      EPINOVA-IMP-2025-001    -> epinova.imp.2025.001
    """
    normalized = normalize_epinova_id_final_number(epinova_id)
    parts = [p.lower() for p in normalized.split("-") if p]
    return ".".join(parts)


def is_pending_doi_value(value: str) -> bool:
    value = (value or "").strip()

    pending_values = {
        "",
        "Pending Crossref registration",
        "DOI pending",
        "DOI pending.",
        "Pending",
        "pending",
        "doi pending",
        "doi pending.",
        DOI_PENDING,
        f"DOI: {DOI_PENDING}",
        f"DOI: {DOI_PENDING}.",
    }

    return value in pending_values


def normalize_doi_to_bare(doi: str) -> str:
    doi = (doi or "").strip()

    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "", 1)

    if doi.startswith("http://doi.org/"):
        doi = doi.replace("http://doi.org/", "", 1)

    return doi.strip().rstrip(".")


def normalize_doi_to_url(doi: str) -> str:
    doi = normalize_doi_to_bare(doi)
    if doi.startswith("10."):
        return f"https://doi.org/{doi}"
    return ""


def is_crossref_doi(doi_bare: str) -> bool:
    return normalize_doi_to_bare(doi_bare).startswith(f"{CROSSREF_PREFIX}/")


def current_doi_bare(data: dict[str, Any]) -> str:
    """
    Returns the best available real DOI without https://doi.org/.

    Priority:
    1. top-level data["doi"] if real DOI
    2. crossref["doi"] if real DOI
    3. Crossref DOI derived from suffix only when status says assigned/registered
    """
    top_doi = normalize_doi_to_bare(str(data.get("doi", "")))
    if top_doi.startswith("10."):
        return top_doi

    crossref = data.get("crossref", {})
    if isinstance(crossref, dict):
        cr_doi = normalize_doi_to_bare(str(crossref.get("doi", "")))
        if cr_doi.startswith("10."):
            return cr_doi

        suffix = (crossref.get("crossref_doi_suffix") or "").strip()
        status = (crossref.get("status") or "").strip().lower()
        registration_status = (crossref.get("registration_status") or "").strip().lower()

        if suffix and (
            status in {"registered", "assigned_pending_deposit", "assigned"}
            or registration_status in {"registered", "ready for deposit"}
        ):
            return f"{CROSSREF_PREFIX}/{suffix}"

    return ""


def current_doi_url(data: dict[str, Any]) -> str:
    doi = current_doi_bare(data)
    if doi:
        return f"https://doi.org/{doi}"
    return ""


# =========================================================
# File helpers
# =========================================================

def find_single_pdf(folder: Path) -> Path | None:
    pdfs = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    )

    if not pdfs:
        return None

    if len(pdfs) > 1:
        print(f"Warning: multiple PDFs found in {folder}. Using first: {pdfs[0].name}")

    return pdfs[0]


# =========================================================
# Metadata updates
# =========================================================

def infer_crossref_record_type(data: dict[str, Any]) -> str:
    """
    Infer Crossref record type for internal metadata notes.

    Current EPINOVA rule:
    - Policy Brief / Working Paper / Reports / White Paper / Index Methodology Paper -> report
    - Article -> journal-article
    - Book-only records may remain book only when explicitly not one of the above.
    """
    publication_type = (data.get("publication_type") or "").lower()
    resource_type = (data.get("resource_type") or "").lower()
    category = (data.get("category") or "").lower()

    if "policy brief" in publication_type:
        return "report"

    if "working paper" in publication_type:
        return "report"

    if "report" in publication_type or "report" in resource_type or "reports" in category:
        return "report"

    if "white" in publication_type:
        return "report"

    if "index methodology" in publication_type or "index-methodology" in category:
        return "report"

    if "article" in publication_type or "article" in resource_type or "articles" in category:
        return "journal-article"

    if "book" in publication_type or resource_type == "book":
        return "book"

    return "report"


def ensure_epinova_id_three_digits(data: dict[str, Any]) -> None:
    """
    Pads the final numeric component of epinova_id to 3 digits.

    This function only changes the primary epinova_id field. It does not rewrite
    historical identifiers inside alternate_identifiers or previous_identifiers.
    """
    epinova_id = data.get("epinova_id")
    if not isinstance(epinova_id, str) or not epinova_id.strip():
        return

    normalized = normalize_epinova_id_final_number(epinova_id)
    data["epinova_id"] = normalized


def ensure_doi_status(data: dict[str, Any]) -> None:
    """
    DOI status update.

    Rules:
    - If a real DOI exists, normalize top-level doi to https://doi.org/...
    - If no real DOI exists and top-level doi is empty/pending, keep pending wording
    - Never overwrite a real DOI with pending text
    """
    doi_url = current_doi_url(data)

    if doi_url:
        data["doi"] = doi_url

        crossref = data.setdefault("crossref", {})
        if isinstance(crossref, dict):
            crossref.setdefault("intended_registration_agency", "Crossref")
            crossref.setdefault("record_type", infer_crossref_record_type(data))

            bare = normalize_doi_to_bare(doi_url)
            if not crossref.get("doi"):
                crossref["doi"] = bare

            if is_crossref_doi(bare) and not crossref.get("crossref_doi_suffix"):
                crossref["crossref_doi_suffix"] = bare.split("/", 1)[1]

        return

    current = (data.get("doi") or "").strip()
    if is_pending_doi_value(current):
        data["doi"] = DOI_PENDING


def _norm_person_token(value: str) -> str:
    return re.sub(r"[^a-z]", "", (value or "").lower())


def ensure_creator_orcid_and_name(data: dict[str, Any]) -> None:
    """
    Normalizes EPINOVA author metadata to current publication style:
      Wu, Shaoyuan / given_name Shaoyuan / family_name Wu

    Recognizes old variants such as Wu, Shao-Yuan and given_name Shao-Yuan.
    """
    creators = data.get("creators", [])

    if not isinstance(creators, list):
        return

    for creator in creators:
        if not isinstance(creator, dict):
            continue

        name = str(creator.get("name") or "")
        family = str(creator.get("family_name") or "")
        given = str(creator.get("given_name") or "")

        name_norm = _norm_person_token(name)
        family_norm = _norm_person_token(family)
        given_norm = _norm_person_token(given)

        is_shaoyuan_wu = (
            "wu" in name_norm and "shaoyuan" in name_norm
        ) or (
            family_norm == "wu" and given_norm == "shaoyuan"
        )

        if is_shaoyuan_wu:
            creator["name"] = "Wu, Shaoyuan"
            creator["given_name"] = "Shaoyuan"
            creator["family_name"] = "Wu"
            creator["orcid"] = AUTHOR_ORCID

    copyright_text = data.get("copyright")
    if isinstance(copyright_text, str):
        data["copyright"] = copyright_text.replace("Shao-Yuan Wu", "Shaoyuan Wu")


def ensure_landing_page(data: dict[str, Any]) -> None:
    """
    Ensures a publication landing page only when landing_page is empty.

    Current rule:
    - Do not overwrite existing Zenodo/DataCite DOI landing_page values.
    - Keep EPINOVA publication URLs lowercase.
    - Ensure crossref_url exists, but do not overwrite a non-empty value.
    """
    epinova_id = data.get("epinova_id", "")
    slug = normalize_slug(str(epinova_id))

    if not slug:
        return

    landing_page = f"{PUBLICATION_BASE_URL}/{slug}/"

    if not data.get("landing_page"):
        data["landing_page"] = landing_page

    crossref = data.setdefault("crossref", {})
    if isinstance(crossref, dict) and not crossref.get("crossref_url"):
        crossref["crossref_url"] = data.get("landing_page", landing_page)


def ensure_crossref_suffix(data: dict[str, Any]) -> None:
    epinova_id = data.get("epinova_id", "")
    suffix = doi_suffix_from_epinova_id(str(epinova_id))

    if not suffix:
        return

    crossref = data.setdefault("crossref", {})

    if not isinstance(crossref, dict):
        return

    if not crossref.get("crossref_doi_suffix"):
        crossref["crossref_doi_suffix"] = suffix

    crossref.setdefault("intended_registration_agency", "Crossref")
    crossref.setdefault("record_type", infer_crossref_record_type(data))
    crossref.setdefault("registration_status", "Pending")

    doi_bare = current_doi_bare(data)
    if doi_bare and not crossref.get("doi"):
        crossref["doi"] = doi_bare


def strip_existing_doi_tail(value: str) -> str:
    """
    Removes trailing DOI / DOI URL / pending DOI phrases from citation strings.

    DOI suffixes may contain periods, so the DOI pattern stops at whitespace,
    not at a period.
    """
    if not isinstance(value, str):
        return ""

    value = value.strip()

    doi_url_pattern = r"https?://doi\.org/10\.\S+"
    bare_doi_pattern = r"10\.\S+"

    patterns = [
        rf"\s*DOI:\s*{doi_url_pattern}\.?\s*$",
        rf"\s*{doi_url_pattern}\.?\s*$",
        rf"\s*DOI:\s*{bare_doi_pattern}\.?\s*$",
        rf"\s*{bare_doi_pattern}\.?\s*$",
        r"\s*DOI:\s*To be assigned after Crossref membership approval\.?\s*$",
        r"\s*To be assigned after Crossref membership approval\.?\s*$",
        r"\s*DOI:\s*Pending Crossref registration\.?\s*$",
        r"\s*Pending Crossref registration\.?\s*$",
        r"\s*DOI pending\.?\s*$",
        r"\s*doi pending\.?\s*$",
        r"\s*DOI:\s*$",
        r"\s*DOI\s*$",
        r"\s*doi:\s*$",
        r"\s*doi\s*$",
    ]

    previous = None
    while previous != value:
        previous = value
        for pattern in patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE).strip()

    return value.rstrip()


def update_citations_doi_status(data: dict[str, Any]) -> None:
    """
    Updates recommended_citation and citation_apa.

    recommended_citation:
      appends "DOI: https://doi.org/..."

    citation_apa:
      appends plain DOI URL without "DOI:" label, following APA style.

    If no real DOI exists:
      appends pending DOI wording.
    """
    doi_url = current_doi_url(data)

    for key in ["recommended_citation", "citation_apa"]:
        value = data.get(key)

        if not isinstance(value, str) or not value.strip():
            continue

        value = strip_existing_doi_tail(value)

        if not value.endswith("."):
            value += "."

        if doi_url:
            if key == "citation_apa":
                value += f" {doi_url}."
            else:
                value += f" DOI: {doi_url}."
        else:
            value += f" DOI: {DOI_PENDING}."

        value = re.sub(r"\s+", " ", value).strip()
        data[key] = value


def update_file_links(data: dict[str, Any], folder: Path, metadata_path: Path, root: Path) -> None:
    relative_folder = folder.relative_to(root)
    pdf = find_single_pdf(folder)

    if pdf:
        relative_pdf = pdf.relative_to(root)
        existing_files = data.get("files", [])

        if (
            existing_files
            and isinstance(existing_files, list)
            and isinstance(existing_files[0], dict)
        ):
            file_entry = existing_files[0]
        else:
            file_entry = {
                "label": "Download PDF",
                "content_type": "application/pdf",
                "format": "application/pdf",
                "description": "Full-text PDF of the publication",
            }

        file_entry["filename"] = pdf.name
        file_entry["url"] = github_blob_url(relative_pdf)
        file_entry.setdefault("label", "Download PDF")
        file_entry.setdefault("content_type", "application/pdf")
        file_entry.setdefault("format", "application/pdf")
        file_entry.setdefault("description", "Full-text PDF of the publication")

        data["files"] = [file_entry]
    else:
        print(f"Warning: no PDF found for {metadata_path}")

    data["repository_folder"] = github_tree_url(relative_folder)
    data.setdefault("repository_url", f"https://github.com/{REPO_OWNER}/{REPO_NAME}")


def _has_legacy_identifier_context(notes: str) -> bool:
    text = (notes or "").lower()
    return any(
        marker in text
        for marker in [
            "legacy",
            "previous identifier",
            "previous identifiers",
            "pre-standardization",
            "iwp–25–01",
            "iwp-25-01",
            "epinova-iwp-2025-01",
        ]
    )


def _doi_phrase_for_metadata_source(data: dict[str, Any]) -> str:
    doi_url = current_doi_url(data)
    if not doi_url:
        return "DOI remains pending."

    doi_bare = normalize_doi_to_bare(doi_url)
    crossref = data.get("crossref", {})
    status = ""
    registration_status = ""

    if isinstance(crossref, dict):
        status = (crossref.get("status") or "").strip().lower()
        registration_status = (crossref.get("registration_status") or "").strip().lower()

    if is_crossref_doi(doi_bare):
        if status == "registered" or registration_status == "registered":
            return f"Crossref DOI registered under EPINOVA LLC prefix {CROSSREF_PREFIX}: {doi_url}."
        return f"Crossref DOI assigned under EPINOVA LLC prefix {CROSSREF_PREFIX}: {doi_url}."

    return f"Primary DOI remains the Zenodo/DataCite DOI: {doi_url}."


def ensure_metadata_source(data: dict[str, Any]) -> None:
    metadata_source = data.setdefault("metadata_source", {})

    if not isinstance(metadata_source, dict):
        return

    metadata_source.setdefault(
        "source",
        "EPINOVA metadata schema adapted from Zenodo/InvenioRDM-style publication records",
    )
    metadata_source.setdefault("created_by", "EPINOVA LLC")
    metadata_source.setdefault("created_date", data.get("publication_date", str(date.today())))
    metadata_source["last_updated"] = str(date.today())

    existing_notes = metadata_source.get("notes", "")
    base = (
        "PDF supplied publication number, title, subtitle, author, affiliation, date, "
        "abstract or executive summary, references, recommended citation, DOI status, "
        "and disclaimer where available."
    )
    doi_phrase = _doi_phrase_for_metadata_source(data)

    if isinstance(existing_notes, str) and existing_notes.strip():
        # Current rule: never erase custom legacy / previous-identifier notes.
        if _has_legacy_identifier_context(existing_notes):
            return

        # Do not duplicate DOI status phrases.
        if "doi" in existing_notes.lower():
            return

        metadata_source["notes"] = f"{existing_notes.rstrip()} {doi_phrase}"
        return

    metadata_source["notes"] = f"{base} {doi_phrase}"


def ensure_publisher_fields(data: dict[str, Any]) -> None:
    """
    Standardizes publisher fields without destroying detailed institutional identity.
    """
    publisher = (data.get("publisher") or "").strip()

    if not publisher or publisher == "Global AI Governance and Policy Research Center, EPINOVA LLC":
        data["publisher"] = "EPINOVA LLC"
        data.setdefault("publisher_unit", "Global AI Governance and Policy Research Center")

    imprint = data.get("imprint")
    if isinstance(imprint, dict):
        if (
            not imprint.get("publisher")
            or imprint.get("publisher") == "Global AI Governance and Policy Research Center, EPINOVA LLC"
        ):
            imprint["publisher"] = "EPINOVA LLC"

        imprint.setdefault("publisher_unit", "Global AI Governance and Policy Research Center")
        imprint.setdefault(
            "institution",
            "Global AI Governance and Policy Research Center, EPINOVA LLC",
        )


def ensure_pdf_metadata_title(data: dict[str, Any]) -> None:
    """
    Fill pdf_metadata.title if empty, using title + subtitle.
    Does not edit the actual PDF file; only metadata.json.
    """
    pdf_metadata = data.setdefault("pdf_metadata", {})

    if not isinstance(pdf_metadata, dict):
        return

    current_title = (pdf_metadata.get("title") or "").strip()
    if current_title:
        return

    title = (data.get("title") or "").strip()
    subtitle = (data.get("subtitle") or "").strip()

    if title and subtitle:
        pdf_metadata["title"] = f"{title}: {subtitle}"
    elif title:
        pdf_metadata["title"] = title


def normalize_crossref_registered_status(data: dict[str, Any]) -> None:
    """
    If Crossref block says registered, normalize fields.
    If DOI exists but status is not registered, leave status as-is unless empty.
    """
    crossref = data.setdefault("crossref", {})

    if not isinstance(crossref, dict):
        return

    doi_bare = current_doi_bare(data)

    if doi_bare:
        crossref.setdefault("doi", doi_bare)
        crossref.setdefault("deposit_ready", True)
        crossref.setdefault("intended_registration_agency", "Crossref")
        crossref.setdefault("record_type", infer_crossref_record_type(data))

        if is_crossref_doi(doi_bare) and not crossref.get("crossref_doi_suffix"):
            crossref["crossref_doi_suffix"] = doi_bare.split("/", 1)[1]

        status = (crossref.get("status") or "").strip().lower()
        registration_status = (crossref.get("registration_status") or "").strip().lower()

        if status == "registered" or registration_status == "registered":
            crossref["status"] = "registered"
            crossref["registration_status"] = "Registered"
            crossref["deposit_ready"] = True
            if is_crossref_doi(doi_bare):
                crossref["notes"] = (
                    f"Crossref DOI registered under EPINOVA LLC prefix {CROSSREF_PREFIX} "
                    "and resolving to the official EPINOVA landing page."
                )
        elif not status and is_crossref_doi(doi_bare):
            crossref["status"] = "assigned_pending_deposit"
            crossref.setdefault("registration_status", "Ready for deposit")
            crossref.setdefault(
                "notes",
                (
                    f"Crossref DOI assigned under EPINOVA LLC prefix {CROSSREF_PREFIX}. "
                    "The DOI is ready for Crossref metadata deposit."
                ),
            )

    if not crossref.get("crossref_url"):
        landing_page = data.get("landing_page", "")
        if landing_page:
            crossref["crossref_url"] = landing_page


# =========================================================
# Main update function
# =========================================================

def update_metadata(metadata_path: Path, root: Path) -> tuple[bool, dict[str, Any], dict[str, Any]]:
    folder = metadata_path.parent

    with metadata_path.open("r", encoding="utf-8-sig") as f:
        original_data = json.load(f)

    data = copy.deepcopy(original_data)

    ensure_epinova_id_three_digits(data)
    update_file_links(data, folder, metadata_path, root)

    # Preserve existing references.
    data.setdefault("references", [])

    ensure_creator_orcid_and_name(data)
    ensure_landing_page(data)
    ensure_crossref_suffix(data)
    ensure_doi_status(data)
    normalize_crossref_registered_status(data)
    update_citations_doi_status(data)
    ensure_publisher_fields(data)
    ensure_pdf_metadata_title(data)
    ensure_metadata_source(data)

    changed = data != original_data
    return changed, original_data, data


def should_skip(metadata_path: Path, include_articles: bool = False) -> bool:
    parts = set(metadata_path.parts)

    if any(part in DEFAULT_SKIP_PARTS for part in parts):
        return True

    if not include_articles and any(part in ARTICLE_PARTS for part in parts):
        return True

    return False


def write_metadata(metadata_path: Path, data: dict[str, Any]) -> None:
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def collect_metadata_files(root: Path, selected_paths: list[str] | None = None) -> list[Path]:
    if selected_paths:
        files: list[Path] = []
        for raw in selected_paths:
            p = (root / raw).resolve()
            if p.is_file() and p.name == METADATA_NAME:
                files.append(p)
            elif p.is_dir():
                files.extend(sorted(p.rglob(METADATA_NAME)))
            else:
                print(f"Warning: path not found or not usable: {p}")
        return sorted(set(files))

    return sorted(root.rglob(METADATA_NAME))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update EPINOVA metadata.json files under current metadata rules."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root or a path inside the repository. Default: current directory.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes. Without --apply, the script only reports what would change.",
    )
    parser.add_argument(
        "--include-articles",
        action="store_true",
        help="Also process Articles. By default Articles are skipped.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional files or folders to process, relative to repository root.",
    )

    args = parser.parse_args()

    global ROOT
    ROOT = find_repo_root(Path(args.root))

    print(f"Repository root: {ROOT}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Include Articles: {args.include_articles}")

    metadata_files = collect_metadata_files(ROOT, args.paths)

    if not metadata_files:
        print("No metadata.json files found.")
        return

    scanned_count = 0
    changed_count = 0

    for metadata_path in metadata_files:
        if should_skip(metadata_path, include_articles=args.include_articles):
            continue

        scanned_count += 1
        changed, _old, new_data = update_metadata(metadata_path, ROOT)

        if changed:
            changed_count += 1
            if args.apply:
                write_metadata(metadata_path, new_data)
                print(f"Updated: {metadata_path}")
            else:
                print(f"Would update: {metadata_path}")

    print(f"Done. Scanned {scanned_count} metadata files.")
    if args.apply:
        print(f"Updated {changed_count} metadata files.")
    else:
        print(f"Would update {changed_count} metadata files. Use --apply to write changes.")


if __name__ == "__main__":
    main()
