import json
from pathlib import Path
from urllib.parse import quote
from datetime import date

# =========================================================
# EPINOVA Metadata Auto-Updater
# For EPINOVA-Research repository
#
# Functions:
# - Auto-fill PDF filename and GitHub blob URL
# - Auto-fill GitHub repository folder URL
# - Auto-fill pending DOI text
# - Auto-fill Shaoyuan Wu ORCID
# - Auto-fill landing page URL
# - Auto-fill Crossref URL and DOI suffix
# - Standardize pending DOI wording in citation fields
# - Preserve existing references
# =========================================================

REPO_OWNER = "EPINOVALLC"
REPO_NAME = "EPINOVA-Research"
BRANCH = "main"

PUBLICATION_BASE_URL = "https://publications.epinova.org"
METADATA_NAME = "metadata.json"

DOI_PENDING = "To be assigned after Crossref membership approval"
AUTHOR_ORCID = "https://orcid.org/0009-0008-0660-8232"


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


def normalize_slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.replace("–", "-").replace("—", "-").replace("_", "-")
    value = value.replace(" ", "-")
    value = value.replace(".", "-")

    while "--" in value:
        value = value.replace("--", "-")

    return value.strip("-")


def doi_suffix_from_epinova_id(epinova_id: str) -> str:
    cleaned = (epinova_id or "").strip()
    cleaned = cleaned.replace("–", "-").replace("—", "-").replace("_", "-")

    parts = [p.lower() for p in cleaned.split("-") if p]

    if not parts:
        return ""

    return ".".join(parts)


def find_single_pdf(folder: Path) -> Path | None:
    pdfs = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    )

    if not pdfs:
        return None

    if len(pdfs) > 1:
        print(f"Warning: multiple PDFs found in {folder}. Using first: {pdfs[0].name}")

    return pdfs[0]


def ensure_pending_doi(data: dict) -> None:
    current_doi = (data.get("doi") or "").strip()

    pending_values = {
        "",
        "Pending Crossref registration",
        "DOI pending",
        "DOI pending.",
        "Pending",
        "pending",
        "doi pending",
        "doi pending."
    }

    if current_doi in pending_values:
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
    if isinstance(crossref, dict):
        if not crossref.get("crossref_doi_suffix"):
            crossref["crossref_doi_suffix"] = suffix

        crossref.setdefault("intended_registration_agency", "Crossref")
        crossref.setdefault("registration_status", "Pending")


def update_citations_pending_doi(data: dict) -> None:
    replacement = f"DOI: {DOI_PENDING}."

    old_patterns = [
        "DOI pending.",
        "DOI pending",
        "doi pending.",
        "doi pending",
        "Pending Crossref registration.",
        "Pending Crossref registration",
        "To be assigned after Crossref membership approval.",
        "To be assigned after Crossref membership approval"
    ]

    for key in ["recommended_citation", "citation_apa"]:
        value = data.get(key)

        if not isinstance(value, str) or not value.strip():
            continue

        value = value.strip()

        # If the standardized phrase already exists, normalize punctuation only.
        if f"DOI: {DOI_PENDING}" in value:
            if not value.endswith("."):
                value += "."
            data[key] = value
            continue

        # Remove old ending patterns.
        for old in old_patterns:
            if value.endswith(old):
                value = value[: -len(old)].rstrip()
                break

        # Remove dangling DOI labels if present.
        dangling = ["DOI:", "DOI", "doi:", "doi"]
        for item in dangling:
            if value.endswith(item):
                value = value[: -len(item)].rstrip()
                break

        if not value.endswith("."):
            value += "."

        value += f" {replacement}"
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
                "description": "Full-text PDF of the publication"
            }

        file_entry["filename"] = pdf.name
        file_entry["url"] = github_blob_url(relative_pdf)
        file_entry.setdefault("label", "Download PDF")
        file_entry.setdefault("content_type", "application/pdf")
        file_entry.setdefault("description", "Full-text PDF of the publication")

        data["files"] = [file_entry]
    else:
        print(f"Warning: no PDF found for {metadata_path}")

    data["repository_folder"] = github_tree_url(relative_folder)
    data.setdefault("repository_url", f"https://github.com/{REPO_OWNER}/{REPO_NAME}")


def ensure_metadata_source(data: dict) -> None:
    metadata_source = data.setdefault("metadata_source", {})

    if isinstance(metadata_source, dict):
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


def update_metadata(metadata_path: Path) -> None:
    folder = metadata_path.parent

    with metadata_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    update_file_links(data, folder, metadata_path)

    # Do not overwrite existing references.
    data.setdefault("references", [])

    ensure_pending_doi(data)
    ensure_creator_orcid(data)
    ensure_landing_page(data)
    ensure_crossref_suffix(data)
    update_citations_pending_doi(data)
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