import json
import re
from pathlib import Path
from urllib.parse import quote
from datetime import date

# =========================================================
# EPINOVA Metadata Auto-Updater
# For EPINOVA-Research repository
#
# Crossref-aware version
#
# Functions:
# - Auto-fill PDF filename and GitHub blob URL
# - Auto-fill GitHub repository folder URL
# - Auto-fill Shaoyuan Wu ORCID
# - Auto-fill landing page URL
# - Auto-fill Crossref URL and DOI suffix
# - Preserve registered Crossref DOI if present
# - Use pending DOI text only when no real DOI exists
# - Update recommended citation / APA citation with real DOI when available
# - Remove duplicate trailing DOI statements before adding DOI status
# - Preserve existing references
# =========================================================

REPO_OWNER = "EPINOVALLC"
REPO_NAME = "EPINOVA-Research"
BRANCH = "main"

PUBLICATION_BASE_URL = "https://publications.epinova.org"
METADATA_NAME = "metadata.json"

DOI_PENDING = "To be assigned after Crossref membership approval"
AUTHOR_ORCID = "https://orcid.org/0009-0008-0660-8232"

CROSSREF_PREFIX = "10.67037"


# =========================================================
# Path helpers
# =========================================================

def find_repo_root() -> Path:
    current = Path(".").resolve()

    if current.name == REPO_NAME:
        return current

    candidate = current / REPO_NAME
    if candidate.exists() and candidate.is_dir():
        return candidate.resolve()

    for parent in [current] + list(current.parents):
        if parent.name == REPO_NAME:
            return parent.resolve()

    return current


ROOT = find_repo_root()


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


# =========================================================
# DOI / slug helpers
# =========================================================

def normalize_slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.replace("–", "-").replace("—", "-").replace("_", "-")
    value = value.replace(" ", "-")
    value = value.replace(".", "-")

    while "--" in value:
        value = value.replace("--", "-")

    return value.strip("-")


def doi_suffix_from_epinova_id(epinova_id: str) -> str:
    """
    Converts:
      EPINOVA-PB-2026-049 -> epinova.pb.2026.049
      EPINOVA-WP-A-2026-03 -> epinova.wp.a.2026.003

    Normalizes final numeric part to 3 digits:
      49 -> 049
      03 -> 003
      1  -> 001
    """
    cleaned = (epinova_id or "").strip()
    cleaned = cleaned.replace("–", "-").replace("—", "-").replace("_", "-")

    parts = [p.lower() for p in cleaned.split("-") if p]

    if not parts:
        return ""

    if parts[-1].isdigit():
        parts[-1] = parts[-1].zfill(3)

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


def current_doi_bare(data: dict) -> str:
    """
    Returns real DOI without https://doi.org/.

    Priority:
    1. top-level data["doi"]
    2. crossref["doi"]
    3. DOI derived from crossref suffix if status is registered/assigned
    """
    top_doi = normalize_doi_to_bare(data.get("doi", ""))

    if top_doi.startswith("10."):
        return top_doi

    crossref = data.get("crossref", {})
    if isinstance(crossref, dict):
        cr_doi = normalize_doi_to_bare(crossref.get("doi", ""))
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


def current_doi_url(data: dict) -> str:
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

def infer_crossref_record_type(data: dict) -> str:
    """
    Infer Crossref record type for internal metadata notes.
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

    if "book" in publication_type:
        return "book"

    if "article" in publication_type or "article" in resource_type or "articles" in category:
        return "journal-article"

    return "report"


def ensure_doi_status(data: dict) -> None:
    """
    Crossref-aware DOI status update.

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

            if not crossref.get("crossref_doi_suffix") and "/" in bare:
                crossref["crossref_doi_suffix"] = bare.split("/", 1)[1]

        return

    current = (data.get("doi") or "").strip()
    if is_pending_doi_value(current):
        data["doi"] = DOI_PENDING


def ensure_creator_orcid(data: dict) -> None:
    creators = data.get("creators", [])

    if not isinstance(creators, list):
        return

    for creator in creators:
        if not isinstance(creator, dict):
            continue

        name = (creator.get("name") or "").lower()
        family = (creator.get("family_name") or "").lower()
        given = (creator.get("given_name") or "").lower()

        is_shaoyuan_wu = (
            "wu" in name and "shaoyuan" in name
        ) or (
            family == "wu" and given == "shaoyuan"
        )

        if is_shaoyuan_wu:
            creator["orcid"] = AUTHOR_ORCID


def ensure_landing_page(data: dict) -> None:
    epinova_id = data.get("epinova_id", "")
    slug = normalize_slug(epinova_id)

    if not slug:
        return

    landing_page = f"{PUBLICATION_BASE_URL}/{slug}/"

    if not data.get("landing_page"):
        data["landing_page"] = landing_page

    crossref = data.setdefault("crossref", {})
    if isinstance(crossref, dict):
        if not crossref.get("crossref_url"):
            crossref["crossref_url"] = data.get("landing_page", landing_page)


def ensure_crossref_suffix(data: dict) -> None:
    epinova_id = data.get("epinova_id", "")
    suffix = doi_suffix_from_epinova_id(epinova_id)

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

    Handles:
    - DOI: https://doi.org/10.67037/epinova.pb.2026.049.
    - https://doi.org/10.67037/epinova.pb.2026.049.
    - DOI: 10.67037/epinova.pb.2026.049.
    - DOI pending
    - To be assigned after Crossref membership approval

    Key fix:
    DOI suffixes may contain periods, so do NOT use [^\\s.]+.
    """

    if not isinstance(value, str):
        return ""

    value = value.strip()

    # DOI suffix may contain periods, hyphens, underscores, slashes, parentheses, etc.
    # Stop only at whitespace.
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


def update_citations_doi_status(data: dict) -> None:
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


def update_file_links(data: dict, folder: Path, metadata_path: Path) -> None:
    relative_folder = folder.relative_to(ROOT)
    pdf = find_single_pdf(folder)

    if pdf:
        relative_pdf = pdf.relative_to(ROOT)
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
                "description": "Full-text PDF of the publication"
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


def ensure_metadata_source(data: dict) -> None:
    metadata_source = data.setdefault("metadata_source", {})

    if not isinstance(metadata_source, dict):
        return

    metadata_source.setdefault(
        "source",
        "EPINOVA metadata schema adapted from Zenodo/InvenioRDM-style publication records"
    )
    metadata_source.setdefault("created_by", "EPINOVA LLC")
    metadata_source.setdefault(
        "created_date",
        data.get("publication_date", str(date.today()))
    )
    metadata_source["last_updated"] = str(date.today())

    doi_url = current_doi_url(data)
    crossref = data.get("crossref", {})
    status = ""
    if isinstance(crossref, dict):
        status = (crossref.get("status") or "").strip().lower()

    if doi_url:
        if status == "registered":
            doi_phrase = (
                f"Crossref DOI registered under EPINOVA LLC prefix "
                f"{CROSSREF_PREFIX}: {doi_url}."
            )
        else:
            doi_phrase = (
                f"Crossref DOI assigned under EPINOVA LLC prefix "
                f"{CROSSREF_PREFIX}: {doi_url}."
            )

        metadata_source["notes"] = (
            "PDF supplied publication number, title, subtitle, author, affiliation, date, "
            "abstract or executive summary, references, recommended citation, DOI status, "
            "and disclaimer where available. "
            f"{doi_phrase}"
        )
    else:
        metadata_source.setdefault(
            "notes",
            (
                "PDF supplied publication number, title, subtitle, author, affiliation, date, "
                "abstract or executive summary, references, recommended citation, DOI status, "
                "and disclaimer where available. DOI remains pending."
            )
        )


def ensure_publisher_fields(data: dict) -> None:
    """
    Standardizes publisher fields without destroying detailed institutional identity.
    """
    publisher = (data.get("publisher") or "").strip()

    if not publisher or publisher == "Global AI Governance and Policy Research Center, EPINOVA LLC":
        data["publisher"] = "EPINOVA LLC"
        data.setdefault("publisher_unit", "Global AI Governance and Policy Research Center")

    imprint = data.get("imprint")
    if isinstance(imprint, dict):
        if not imprint.get("publisher") or imprint.get("publisher") == "Global AI Governance and Policy Research Center, EPINOVA LLC":
            imprint["publisher"] = "EPINOVA LLC"

        imprint.setdefault("publisher_unit", "Global AI Governance and Policy Research Center")
        imprint.setdefault(
            "institution",
            "Global AI Governance and Policy Research Center, EPINOVA LLC"
        )


def ensure_pdf_metadata_title(data: dict) -> None:
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


def normalize_crossref_registered_status(data: dict) -> None:
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

        if not crossref.get("crossref_doi_suffix") and "/" in doi_bare:
            crossref["crossref_doi_suffix"] = doi_bare.split("/", 1)[1]

        status = (crossref.get("status") or "").strip().lower()
        registration_status = (crossref.get("registration_status") or "").strip().lower()

        if status == "registered" or registration_status == "registered":
            crossref["status"] = "registered"
            crossref["registration_status"] = "Registered"
            crossref["deposit_ready"] = True
            crossref["notes"] = (
                f"Crossref DOI registered under EPINOVA LLC prefix {CROSSREF_PREFIX} "
                "and resolving to the official EPINOVA landing page."
            )
        elif not status:
            crossref["status"] = "assigned_pending_deposit"
            crossref.setdefault("registration_status", "Ready for deposit")
            crossref.setdefault(
                "notes",
                (
                    f"Crossref DOI assigned under EPINOVA LLC prefix {CROSSREF_PREFIX}. "
                    "The DOI is ready for Crossref metadata deposit."
                )
            )

    if not crossref.get("crossref_url"):
        landing_page = data.get("landing_page", "")
        if landing_page:
            crossref["crossref_url"] = landing_page


# =========================================================
# Main update function
# =========================================================

def update_metadata(metadata_path: Path) -> None:
    folder = metadata_path.parent

    with metadata_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    update_file_links(data, folder, metadata_path)

    # Preserve existing references.
    data.setdefault("references", [])

    ensure_creator_orcid(data)
    ensure_landing_page(data)
    ensure_crossref_suffix(data)
    ensure_doi_status(data)
    normalize_crossref_registered_status(data)
    update_citations_doi_status(data)
    ensure_publisher_fields(data)
    ensure_pdf_metadata_title(data)
    ensure_metadata_source(data)

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated: {metadata_path}")


def should_skip(metadata_path: Path) -> bool:
    skip_parts = {"docs", "site", "generated", ".git", "__pycache__"}
    return any(part in skip_parts for part in metadata_path.parts)


def main() -> None:
    print(f"Repository root: {ROOT}")

    metadata_files = list(ROOT.rglob(METADATA_NAME))

    if not metadata_files:
        print("No metadata.json files found.")
        return

    updated_count = 0

    for metadata_path in metadata_files:
        if should_skip(metadata_path):
            continue

        update_metadata(metadata_path)
        updated_count += 1

    print(f"Done. Updated {updated_count} metadata files.")


if __name__ == "__main__":
    main()