import json
import shutil
from pathlib import Path
from html import escape
from urllib.parse import quote
from datetime import date
from collections import defaultdict

# =========================================================
# EPINOVA Landing Page Generator
# Zenodo-like static record page
# For EPINOVA-Research repository
#
# Reads all metadata.json files and generates:
# - docs/index.html
# - docs/<category>/index.html
# - docs/<epinova-id-slug>/index.html
# - docs/assets/global-ai-governance-logo.png
# =========================================================

REPO_NAME = "EPINOVA-Research"
METADATA_NAME = "metadata.json"

SITE_TITLE = "EPINOVA Publications"
SITE_BASE_URL = "https://publications.epinova.org"
EPINOVA_MAIN_SITE = "https://epinova.org"

CENTER_NAME = "Global AI Governance and Policy Research Center"
PUBLISHER_NAME = "Global AI Governance and Policy Research Center, EPINOVA LLC"

OUTPUT_DIR_NAME = "docs"

LOGO_CANDIDATES = [
    "assets/global-ai-governance-logo.png",
    "assets/global-ai-governance-logo.jpg",
    "assets/global-ai-governance-logo.webp",
    "assets/logo.png",
    "assets/logo.jpg"
]

OUTPUT_LOGO_PATH = "assets/global-ai-governance-logo.png"

CATEGORY_ORDER = [
    "articles",
    "policy-briefs",
    "working-papers",
    "reports",
    "white-books",
]

CATEGORY_LABELS = {
    "articles": "Articles",
    "policy-briefs": "Policy Briefs",
    "working-papers": "Working Papers",
    "reports": "Reports",
    "white-books": "White Books",
    "other": "Other",
    "uncategorized": "Uncategorized"
}

SKIP_PARTS = {"docs", "site", "generated", ".git", "__pycache__"}


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
OUTPUT_DIR = ROOT / OUTPUT_DIR_NAME


def h(value) -> str:
    return escape(str(value or ""), quote=True)


def normalize_slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.replace("–", "-").replace("—", "-").replace("_", "-")
    value = value.replace(" ", "-")
    value = value.replace(".", "-")
    value = value.replace("/", "-")
    value = value.replace("\\", "-")

    allowed = []
    for ch in value:
        if ch.isalnum() or ch == "-":
            allowed.append(ch)

    value = "".join(allowed)

    while "--" in value:
        value = value.replace("--", "-")

    return value.strip("-")


def get_slug(meta: dict) -> str:
    epinova_id = meta.get("epinova_id", "")
    if epinova_id:
        return normalize_slug(epinova_id)

    title = meta.get("title", "")
    return normalize_slug(title)[:90] or "untitled"


def should_skip(metadata_path: Path) -> bool:
    return any(part in SKIP_PARTS for part in metadata_path.parts)


def load_metadata_files() -> list[dict]:
    records = []

    for path in sorted(ROOT.rglob(METADATA_NAME)):
        if should_skip(path):
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as exc:
            print(f"Warning: failed to read {path}: {exc}")
            continue

        meta["_metadata_path"] = str(path.relative_to(ROOT))
        meta["_metadata_abs_path"] = str(path)
        meta["_slug"] = get_slug(meta)
        meta["_page_url"] = f"{SITE_BASE_URL}/{meta['_slug']}/"

        records.append(meta)

    records.sort(
        key=lambda r: (
            r.get("publication_date", ""),
            r.get("epinova_id", ""),
            r.get("title", "")
        ),
        reverse=True
    )

    return records


def first_creator(meta: dict) -> str:
    creators = meta.get("creators", [])
    if isinstance(creators, list) and creators:
        first = creators[0]
        if isinstance(first, dict):
            return first.get("name", "")
        return str(first)
    return meta.get("author", "")


def all_creators_plain(meta: dict) -> list[str]:
    creators = meta.get("creators", [])
    names = []

    if isinstance(creators, list):
        for creator in creators:
            if isinstance(creator, dict):
                name = creator.get("name", "")
                if name:
                    names.append(name)
            elif creator:
                names.append(str(creator))

    return names


def github_blob_to_raw_url(url: str) -> str:
    """
    Convert GitHub blob URL to raw.githubusercontent.com URL.

    Example:
    https://github.com/OWNER/REPO/blob/main/path/file.pdf
    ->
    https://raw.githubusercontent.com/OWNER/REPO/main/path/file.pdf
    """
    if not isinstance(url, str):
        return ""

    prefix = "https://github.com/"
    if not url.startswith(prefix) or "/blob/" not in url:
        return url

    rest = url[len(prefix):]

    try:
        owner_repo, path_part = rest.split("/blob/", 1)
    except ValueError:
        return url

    return f"https://raw.githubusercontent.com/{owner_repo}/{path_part}"

def local_file_url(meta: dict, filename: str, absolute: bool = False) -> str:
    """
    Return local static PDF URL under docs/files/<slug>/<filename>.
    """
    slug = meta.get("_slug", "untitled")
    encoded_filename = quote(filename, safe="")
    path = f"/files/{slug}/{encoded_filename}"

    if absolute:
        return f"{SITE_BASE_URL}{path}"

    return path


def copy_record_files(meta: dict) -> None:
    """
    Copy publication files from the metadata folder into docs/files/<slug>/.
    This makes PDFs available from the same domain as the landing page,
    allowing iframe preview to work reliably.
    """
    metadata_abs_path = meta.get("_metadata_abs_path")
    if not metadata_abs_path:
        return

    source_dir = Path(metadata_abs_path).parent
    slug = meta.get("_slug", "untitled")
    target_dir = OUTPUT_DIR / "files" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    files = meta.get("files", [])
    if not isinstance(files, list):
        return

    for file_entry in files:
        if not isinstance(file_entry, dict):
            continue

        filename = file_entry.get("filename", "")
        if not filename:
            continue

        source_file = source_dir / filename
        target_file = target_dir / filename

        if source_file.exists() and source_file.is_file():
            shutil.copy2(source_file, target_file)
        else:
            print(f"Warning: source file not found: {source_file}")


def is_pdf_filename(filename: str) -> bool:
    return filename.lower().endswith(".pdf")

def first_pdf_url(meta: dict) -> str:
    """
    Absolute PDF URL for citation metadata.
    Uses the site-hosted PDF copy instead of GitHub.
    """
    files = meta.get("files", [])
    if isinstance(files, list):
        for item in files:
            if isinstance(item, dict):
                filename = item.get("filename", "")
                if filename and is_pdf_filename(filename):
                    return local_file_url(meta, filename, absolute=True)
    return ""


def meta_value(meta: dict, key: str, fallback: str = "Not specified") -> str:
    value = meta.get(key, "")
    if value is None or value == "":
        return fallback
    return str(value)


def linkify_urls(text: str) -> str:
    parts = text.split()
    out = []

    for part in parts:
        clean = part.rstrip(".,);]")
        suffix = part[len(clean):]

        if clean.startswith("https://") or clean.startswith("http://"):
            out.append(f'<a href="{clean}">{clean}</a>{suffix}')
        else:
            out.append(part)

    return " ".join(out)


def creators_html(meta: dict) -> str:
    creators = meta.get("creators", [])

    if not isinstance(creators, list) or not creators:
        return "<p class='muted'>No creator information provided.</p>"

    items = []

    for creator in creators:
        if not isinstance(creator, dict):
            items.append(f"<li>{h(creator)}</li>")
            continue

        name = creator.get("name", "")
        affiliation = creator.get("affiliation", "")
        orcid = creator.get("orcid", "")

        line = [f"<strong>{h(name)}</strong>"]

        if affiliation:
            line.append(f"<br><span class='muted'>{h(affiliation)}</span>")

        if orcid:
            if str(orcid).startswith("http"):
                line.append(f"<br><a href='{h(orcid)}'>{h(orcid)}</a>")
            else:
                line.append(f"<br><span class='muted'>{h(orcid)}</span>")

        items.append(f"<li>{''.join(line)}</li>")

    return "<ul class='plain-list'>" + "\n".join(items) + "</ul>"


def list_html(values) -> str:
    if not values:
        return "<p class='muted'>Not specified.</p>"

    if isinstance(values, str):
        return f"<p>{h(values)}</p>"

    if isinstance(values, list):
        items = []
        for item in values:
            if isinstance(item, dict):
                label = (
                    item.get("title")
                    or item.get("name")
                    or item.get("identifier")
                    or str(item)
                )
                items.append(f"<li>{h(label)}</li>")
            else:
                items.append(f"<li>{h(item)}</li>")
        return "<ul>" + "\n".join(items) + "</ul>"

    return f"<p>{h(values)}</p>"


def references_html(meta: dict) -> str:
    refs = meta.get("references", [])

    if not refs:
        return "<p class='muted'>No references listed.</p>"

    items = []
    for ref in refs:
        items.append(f"<li>{linkify_urls(h(ref))}</li>")

    return "<ol class='references'>" + "\n".join(items) + "</ol>"


def file_preview_html(meta: dict) -> str:
    files = meta.get("files", [])

    if not isinstance(files, list) or not files:
        return """
<section class="record-section">
  <h2>Files</h2>
  <p class="muted">No files listed.</p>
</section>
"""

    first = None
    for item in files:
        if isinstance(item, dict):
            first = item
            break

    if not first:
        return """
<section class="record-section">
  <h2>Files</h2>
  <p class="muted">No files listed.</p>
</section>
"""

    filename = first.get("filename", "Publication file")
    url = first.get("url", "")


    preview = ""
    if filename and is_pdf_filename(filename):
        preview_url = local_file_url(meta, filename)
        preview = f"""
<div class="file-preview">
  <div class="file-preview-title">PDF preview</div>
  <iframe src="{h(preview_url)}" title="{h(filename)}"></iframe>
</div>
"""

    table_rows = []
    for file_entry in files:
        if not isinstance(file_entry, dict):
            continue

        fn = file_entry.get("filename", "File")
        file_url = file_entry.get("url", "")
        file_type = file_entry.get("content_type", "")
        desc = file_entry.get("description", "")

        if fn:
            download_url = local_file_url(meta, fn)
            name_html = f"<a href='{h(download_url)}'>{h(fn)}</a>"
            action_html = f"<a class='button small' href='{h(download_url)}'>Download</a>"
        else:
            name_html = h(fn)
            action_html = ""

        table_rows.append(
            "<tr>"
            f"<td>{name_html}<br><span class='muted'>{h(desc)}</span></td>"
            f"<td>{h(file_type)}</td>"
            f"<td class='right'>{action_html}</td>"
            "</tr>"
        )

    return f"""
<section class="record-section">
  <h2>Files</h2>
  {preview}
  <div class="panel">
    <div class="panel-heading">Files</div>
    <table class="file-table">
      <thead>
        <tr><th>Name</th><th>Type</th><th></th></tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </div>
</section>
"""


def alternate_ids_html(meta: dict) -> str:
    ids = meta.get("alternate_identifiers", [])

    if not isinstance(ids, list) or not ids:
        return "<p class='muted'>No alternate identifiers listed.</p>"

    rows = []

    for item in ids:
        if not isinstance(item, dict):
            continue

        identifier = item.get("identifier", "")
        scheme = item.get("scheme", "")
        description = item.get("description", "")

        if identifier.startswith("http"):
            identifier_html = f"<a href='{h(identifier)}'>{h(identifier)}</a>"
        elif scheme.upper() == "DOI":
            identifier_html = f"<a href='https://doi.org/{h(identifier)}'>{h(identifier)}</a>"
        else:
            identifier_html = h(identifier)

        rows.append(
            "<tr>"
            f"<td>{h(scheme)}</td>"
            f"<td>{identifier_html}</td>"
            f"<td>{h(description)}</td>"
            "</tr>"
        )

    return (
        "<table>"
        "<thead><tr><th>Scheme</th><th>Identifier</th><th>Description</th></tr></thead>"
        "<tbody>"
        + "\n".join(rows)
        + "</tbody></table>"
    )


def related_works_html(meta: dict) -> str:
    works = meta.get("related_works", [])

    if not isinstance(works, list) or not works:
        return "<p class='muted'>No related works listed.</p>"

    rows = []

    for item in works:
        if not isinstance(item, dict):
            continue

        relation = item.get("relation", "")
        identifier = item.get("identifier", "")
        scheme = item.get("scheme", "")
        resource_type = item.get("resource_type", "")
        description = item.get("description", "")

        if identifier.startswith("http"):
            identifier_html = f"<a href='{h(identifier)}'>{h(identifier)}</a>"
        elif scheme.upper() == "DOI":
            identifier_html = f"<a href='https://doi.org/{h(identifier)}'>{h(identifier)}</a>"
        else:
            identifier_html = h(identifier)

        rows.append(
            "<tr>"
            f"<td>{h(relation)}</td>"
            f"<td>{identifier_html}</td>"
            f"<td>{h(resource_type)}</td>"
            f"<td>{h(description)}</td>"
            "</tr>"
        )

    return (
        "<table>"
        "<thead><tr><th>Relation</th><th>Identifier</th><th>Type</th><th>Description</th></tr></thead>"
        "<tbody>"
        + "\n".join(rows)
        + "</tbody></table>"
    )


def sidebar_details_html(meta: dict) -> str:
    doi = meta_value(meta, "doi", "")
    previous_doi = meta_value(meta, "previous_doi", "")
    resource_type = meta_value(meta, "resource_type", "")
    publication_type = meta_value(meta, "publication_type", "")
    publisher = meta_value(meta, "publisher", "")
    publication_date = meta_value(meta, "publication_date", "")
    version = meta_value(meta, "version", "")
    epinova_id = meta_value(meta, "epinova_id", "")
    status = meta_value(meta, "status", "")
    language = meta_value(meta, "language", "")
    place = meta_value(meta, "place", "")

    doi_html = h(doi)
    if doi.startswith("http"):
        doi_html = f"<a href='{h(doi)}'>{h(doi)}</a>"

    previous_doi_html = ""
    if previous_doi:
        previous_doi_html = (
            f"<dt>Previous DOI</dt>"
            f"<dd><a href='https://doi.org/{h(previous_doi)}'>{h(previous_doi)}</a></dd>"
        )

    return f"""
<div class="sidebar-box">
  <h2>Details</h2>
  <dl class="details-list">
    <dt>DOI</dt>
    <dd>{doi_html}</dd>
    {previous_doi_html}
    <dt>EPINOVA ID</dt>
    <dd>{h(epinova_id)}</dd>
    <dt>Resource type</dt>
    <dd>{h(resource_type)}</dd>
    <dt>Publication type</dt>
    <dd>{h(publication_type)}</dd>
    <dt>Publication date</dt>
    <dd>{h(publication_date)}</dd>
    <dt>Version</dt>
    <dd>{h(version)}</dd>
    <dt>Status</dt>
    <dd>{h(status)}</dd>
    <dt>Language</dt>
    <dd>{h(language)}</dd>
    <dt>Publisher</dt>
    <dd>{h(publisher)}</dd>
    <dt>Place</dt>
    <dd>{h(place)}</dd>
  </dl>
</div>
"""


def sidebar_rights_html(meta: dict) -> str:
    license_data = meta.get("license", {})
    if isinstance(license_data, dict):
        license_title = license_data.get("title", "")
        license_url = license_data.get("url", "")
    else:
        license_title = str(license_data)
        license_url = ""

    if license_url:
        license_html = f"<a href='{h(license_url)}'>{h(license_title)}</a>"
    else:
        license_html = h(license_title or "Not specified")

    copyright_text = meta_value(meta, "copyright", "")

    return f"""
<div class="sidebar-box">
  <h2>Rights</h2>
  <dl class="details-list">
    <dt>License</dt>
    <dd>{license_html}</dd>
    <dt>Copyright</dt>
    <dd>{h(copyright_text)}</dd>
  </dl>
</div>
"""


def sidebar_citation_html(meta: dict) -> str:
    citation = meta_value(meta, "citation_apa", "")
    if not citation:
        citation = meta_value(meta, "recommended_citation", "")

    return f"""
<div class="sidebar-box">
  <h2>Citation</h2>
  <p class="citation-text">{h(citation)}</p>
</div>
"""


def sidebar_export_html(meta: dict) -> str:
    metadata_path = meta.get("_metadata_path", "")
    repository_folder = meta_value(meta, "repository_folder", "")
    official_page = meta_value(meta, "official_page", "")

    items = []

    if repository_folder:
        items.append(f"<li><a href='{h(repository_folder)}'>Repository folder</a></li>")

    if official_page:
        items.append(f"<li><a href='{h(official_page)}'>Official EPINOVA page</a></li>")

    if metadata_path:
        items.append(f"<li><span class='muted'>Metadata path:</span><br>{h(metadata_path)}</li>")

    if not items:
        items.append("<li class='muted'>No export links listed.</li>")

    return f"""
<div class="sidebar-box">
  <h2>Export</h2>
  <ul class="sidebar-links">
    {''.join(items)}
  </ul>
</div>
"""


def page_css() -> str:
    return """
:root {
  --text: #202020;
  --muted: #666;
  --border: #d9d9d9;
  --soft: #f7f7f7;
  --soft2: #fbfbfb;
  --link: #0b5cad;
  --dark: #050505;
  --dark2: #111;
  --green: #2f7d32;
}

* {
  box-sizing: border-box;
}

html {
  background: #fff;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: var(--text);
  background: #fff;
  line-height: 1.55;
}

a {
  color: var(--link);
  overflow-wrap: anywhere;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.topbar {
  background: var(--dark);
  color: #fff;
  border-bottom: 1px solid #222;
}

.topbar-inner {
  max-width: 1180px;
  min-height: 96px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-only-header {
  justify-content: center;
}

.brand-logo-wrap {
  width: 620px;
  height: 88px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-logo {
  width: 560px;
  height: auto;
  max-height: none;
  object-fit: contain;
  display: block;
  transform: translateX(-18px) scale(1.05);
  transform-origin: center center;
}

.publication-nav-bar {
  width: 100%;
  background: #f4f4f4;
  border-top: 1px solid #d6d6d6;
  border-bottom: 1px solid #d6d6d6;
}

.publication-nav {
  max-width: 1180px;
  margin: 0 auto;
  padding: 11px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 34px;
}

.publication-nav a {
  color: #222222;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;
}

.publication-nav a:hover {
  color: #0b5cad;
  text-decoration: none;
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 32px 24px 48px;
}

.record-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 34px;
  align-items: start;
}

.record-main {
  min-width: 0;
}

.record-sidebar {
  min-width: 0;
}

.record-info-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin-bottom: 20px;
  color: var(--muted);
  font-size: 14px;
}

.label-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: #f1f1f1;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  color: #333;
}

.label-open {
  color: var(--green);
  border-color: #b6d7b9;
  background: #f5fbf5;
}

h1 {
  font-size: 34px;
  line-height: 1.22;
  margin: 0 0 16px;
  font-weight: 700;
}

h2 {
  font-size: 22px;
  line-height: 1.3;
  margin: 32px 0 12px;
}

h3 {
  font-size: 17px;
  margin: 0 0 10px;
}

.record-section {
  margin-top: 28px;
}

.creators {
  margin-bottom: 22px;
}

.plain-list {
  padding-left: 20px;
}

.muted {
  color: var(--muted);
}

.rich-text {
  word-wrap: break-word;
  overflow-wrap: anywhere;
}

.panel {
  border: 1px solid var(--border);
  border-radius: 4px;
  background: #fff;
  margin-top: 14px;
  overflow: hidden;
}

.panel-heading {
  background: var(--soft);
  border-bottom: 1px solid var(--border);
  padding: 10px 14px;
  font-weight: 700;
}

.file-preview {
  border: 1px solid var(--border);
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
  margin: 14px 0;
}

.file-preview-title {
  background: var(--soft);
  border-bottom: 1px solid var(--border);
  padding: 10px 14px;
  font-weight: 700;
}

.file-preview iframe {
  width: 100%;
  height: 620px;
  border: 0;
  background: #eee;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  border-top: 1px solid var(--border);
  padding: 9px 10px;
  text-align: left;
  vertical-align: top;
}

thead th {
  background: var(--soft);
  border-top: 0;
}

.file-table td.right {
  text-align: right;
  white-space: nowrap;
}

.button {
  display: inline-block;
  border: 1px solid #777;
  border-radius: 4px;
  padding: 7px 11px;
  color: #111;
  background: #fff;
  text-decoration: none;
}

.button:hover {
  border-color: #111;
  text-decoration: none;
}

.button.small {
  padding: 4px 8px;
  font-size: 13px;
}

.sidebar-box {
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 4px;
  margin-bottom: 18px;
  overflow: hidden;
}

.sidebar-box h2 {
  margin: 0;
  font-size: 17px;
  padding: 12px 14px;
  background: var(--soft);
  border-bottom: 1px solid var(--border);
}

.details-list {
  margin: 0;
  padding: 14px;
}

.details-list dt {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 12px;
  font-weight: 700;
}

.details-list dt:first-child {
  margin-top: 0;
}

.details-list dd {
  margin: 4px 0 0;
  overflow-wrap: anywhere;
}

.sidebar-links {
  margin: 0;
  padding: 14px 14px 14px 32px;
}

.citation-text {
  margin: 0;
  padding: 14px;
  font-size: 14px;
  overflow-wrap: anywhere;
}

.references li {
  margin-bottom: 8px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.card {
  display: block;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 18px;
  color: var(--text);
  background: #fff;
}

.card:hover {
  border-color: #111;
  text-decoration: none;
}

.latest-list li,
.category-list li {
  margin-bottom: 10px;
}

.footer {
  background: var(--dark);
  color: #ccc;
  margin-top: 48px;
}

.footer-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px 24px;
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 24px;
  font-size: 14px;
}

.footer h2 {
  color: #fff;
  border: 0;
  padding: 0;
  margin: 0 0 10px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.footer a {
  color: #fff;
}

.footer-bottom {
  border-top: 1px solid #222;
  padding-top: 14px;
  margin-top: 14px;
  grid-column: 1 / -1;
  color: #aaa;
  font-size: 13px;
}

.small {
  font-size: 13px;
}

@media (max-width: 900px) {
  .record-grid {
    grid-template-columns: 1fr;
  }

  .topbar-inner {
    max-width: 1180px;
    min-height: 108px;
    margin: 0 auto;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-only-header {
    justify-content: center;
  }

  .brand-logo-wrap {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
  }

  .brand-logo {
    width: min(400px, 92vw);
    height: auto;
    max-height: 62px;
    transform: none;
  }

  .publication-nav {
    flex-wrap: wrap;
    gap: 10px 20px;
    padding: 10px 16px;
  }

  .publication-nav a {
    font-size: 12px;
    letter-spacing: 0.04em;
  }

  h1 {
    font-size: 28px;
  }

  .file-preview iframe {
    height: 460px;
  }

  .footer-inner {
    grid-template-columns: 1fr;
  }
}
"""


def head_meta(meta: dict | None = None, title: str = SITE_TITLE) -> str:
    if not meta:
        return f"""
  <meta name="description" content="{h(SITE_TITLE)}">
  <meta property="og:title" content="{h(SITE_TITLE)}">
  <meta property="og:site_name" content="{h(SITE_TITLE)}">
"""

    page_url = meta.get("_page_url", "")
    record_title = meta.get("title", title)
    description = meta.get("abstract") or meta.get("description") or record_title
    doi = meta.get("doi", "")
    pdf_url = first_pdf_url(meta)
    creators = all_creators_plain(meta)

    citation_authors = "\n".join(
        f'  <meta name="citation_author" content="{h(name)}">'
        for name in creators
    )

    citation_doi = ""
    if doi and not doi.startswith("To be assigned"):
        citation_doi = f'  <meta name="citation_doi" content="{h(doi.replace("https://doi.org/", ""))}">'

    citation_pdf = ""
    if pdf_url:
        citation_pdf = f"""
  <meta name="citation_pdf_url" content="{h(pdf_url)}">
  <link rel="alternate" type="application/pdf" href="{h(pdf_url)}">
  <link rel="item" type="application/pdf" href="{h(pdf_url)}">
"""

    return f"""
  <meta name="description" content="{h(description)}">
  <meta name="citation_title" content="{h(record_title)}">
{citation_authors}
{citation_doi}
  <meta name="citation_publication_date" content="{h(meta.get("publication_date", ""))}">
  <meta name="citation_abstract_html_url" content="{h(page_url)}">
{citation_pdf}
  <meta property="og:title" content="{h(record_title)}">
  <meta property="og:description" content="{h(description)}">
  <meta property="og:url" content="{h(page_url)}">
  <meta property="og:site_name" content="{h(SITE_TITLE)}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{h(record_title)}">
  <meta name="twitter:description" content="{h(description)}">
  <link rel="canonical" href="{h(page_url)}">
"""


def schema_json_ld(meta: dict | None = None) -> str:
    if not meta:
        return ""

    creators = []
    for name in all_creators_plain(meta):
        creators.append({"@type": "Person", "name": name})

    license_url = ""
    license_data = meta.get("license", {})
    if isinstance(license_data, dict):
        license_url = license_data.get("url", "")

    identifier = meta.get("doi", "")
    if identifier and not identifier.startswith("http") and not identifier.startswith("To be assigned"):
        identifier = f"https://doi.org/{identifier}"

    if identifier.startswith("To be assigned"):
        identifier = meta.get("_page_url", "")

    data = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "@id": identifier or meta.get("_page_url", ""),
        "name": meta.get("title", ""),
        "headline": meta.get("title", ""),
        "description": meta.get("abstract") or meta.get("description", ""),
        "datePublished": meta.get("publication_date", ""),
        "version": meta.get("version", ""),
        "identifier": identifier or meta.get("epinova_id", ""),
        "url": meta.get("_page_url", ""),
        "author": creators,
        "creator": creators,
        "publisher": {
            "@type": "Organization",
            "name": meta.get("publisher", PUBLISHER_NAME)
        }
    }

    if license_url:
        data["license"] = license_url

    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False)
        + "</script>"
    )


def site_header() -> str:
    return f"""
<header class="topbar">
  <div class="topbar-inner logo-only-header">
    <div class="brand-logo-wrap">
      <img
        class="brand-logo"
        src="/{h(OUTPUT_LOGO_PATH)}"
        alt="Global AI Governance and Policy Research Center, EPINOVA LLC"
      >
    </div>
  </div>
</header>

<div class="publication-nav-bar">
  <nav class="publication-nav" aria-label="Publication navigation">
    <a href="/">Publications</a>
    <a href="/policy-briefs/">Policy Briefs</a>
    <a href="/working-papers/">Working Papers</a>
    <a href="/reports/">Reports</a>
    <a href="/white-books/">White Books</a>
    <a href="{h(EPINOVA_MAIN_SITE)}">EPINOVA</a>
  </nav>
</div>
"""


def site_footer() -> str:
    return f"""
<footer class="footer">
  <div class="footer-inner">
    <div>
      <h2>About</h2>
      <p>{h(CENTER_NAME)} publishes structured open-access research outputs through EPINOVA LLC.</p>
    </div>
    <div>
      <h2>Publications</h2>
      <p><a href="/">Publication index</a><br>
      <a href="/policy-briefs/">Policy Briefs</a><br>
      <a href="/working-papers/">Working Papers</a><br>
      <a href="/reports/">Reports</a><br>
      <a href="/white-books/">White Books</a></p>
    </div>
    <div>
      <h2>Links</h2>
      <p><a href="{h(EPINOVA_MAIN_SITE)}">EPINOVA main site</a><br>
      <a href="https://github.com/EPINOVALLC/EPINOVA-Research">GitHub repository</a></p>
    </div>
    <div class="footer-bottom">
      Generated on {date.today().isoformat()} from EPINOVA metadata records.
    </div>
  </div>
</footer>
"""


def html_doc(title: str, body: str, meta: dict | None = None) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{h(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
{head_meta(meta, title)}
  <style>{page_css()}</style>
{schema_json_ld(meta)}
</head>
<body>
{site_header()}
{body}
{site_footer()}
</body>
</html>
"""


def render_record_page(meta: dict) -> str:
    title = meta_value(meta, "title")
    publication_type = meta_value(meta, "publication_type")
    publication_date = meta_value(meta, "publication_date")
    version = meta_value(meta, "version")
    status = meta_value(meta, "status")
    abstract = meta_value(meta, "abstract", "")
    description = meta_value(meta, "description", "")
    recommended_citation = meta_value(meta, "recommended_citation", "")
    citation_apa = meta_value(meta, "citation_apa", "")

    body = f"""
<main class="container">
  <div class="record-grid">
    <article class="record-main">
      <section class="record-info-row" aria-label="Publication date and version number">
        <div>
          <span title="Publication date">Published {h(publication_date)}</span>
          <span class="muted"> | Version {h(version)}</span>
        </div>
        <div class="label-group">
          <span class="label">{h(publication_type)}</span>
          <span class="label label-open">Open</span>
          <span class="label">{h(status)}</span>
        </div>
      </section>

      <section aria-label="Record title, authors and contributors">
        <h1>{h(title)}</h1>
        <div class="creators">
          {creators_html(meta)}
        </div>
      </section>

      <section class="record-section rich-text" aria-label="Record description">
        <h2>Description</h2>
        <p>{h(description)}</p>
      </section>

      <section class="record-section rich-text" aria-label="Abstract">
        <h2>Abstract</h2>
        <p>{h(abstract)}</p>
      </section>

      {file_preview_html(meta)}

      <section class="record-section">
        <h2>Keywords</h2>
        {list_html(meta.get("keywords", []))}
      </section>

      <section class="record-section">
        <h2>Subjects</h2>
        {list_html(meta.get("subjects", []))}
      </section>

      <section class="record-section">
        <h2>Recommended citation</h2>
        <p>{h(recommended_citation)}</p>
      </section>

      <section class="record-section">
        <h2>APA citation</h2>
        <p>{h(citation_apa)}</p>
      </section>

      <section class="record-section">
        <h2>Alternate identifiers</h2>
        {alternate_ids_html(meta)}
      </section>

      <section class="record-section">
        <h2>Related works</h2>
        {related_works_html(meta)}
      </section>

      <section class="record-section">
        <h2>References</h2>
        {references_html(meta)}
      </section>
    </article>

    <aside class="record-sidebar" aria-label="Record details">
      {sidebar_details_html(meta)}
      {sidebar_rights_html(meta)}
      {sidebar_citation_html(meta)}
      {sidebar_export_html(meta)}
    </aside>
  </div>
</main>
"""
    return html_doc(f"{title} | {SITE_TITLE}", body, meta)


def render_index_page(records: list[dict]) -> str:
    category_counts = defaultdict(int)

    for meta in records:
        category_counts[meta.get("category", "uncategorized") or "uncategorized"] += 1

    cards = []

    for category in CATEGORY_ORDER:
        label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())
        count = category_counts.get(category, 0)
        cards.append(
            f"""
<a class="card" href="/{h(category)}/">
  <h2>{h(label)}</h2>
  <p>{count} publication{'s' if count != 1 else ''}</p>
</a>
"""
        )

    for category in sorted(category_counts.keys()):
        if category in CATEGORY_ORDER:
            continue
        label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())
        count = category_counts.get(category, 0)
        cards.append(
            f"""
<a class="card" href="/{h(category)}/">
  <h2>{h(label)}</h2>
  <p>{count} publication{'s' if count != 1 else ''}</p>
</a>
"""
        )

    latest_items = []
    for meta in records[:30]:
        latest_items.append(
            f"""
<li>
  <strong>{h(meta.get("epinova_id", ""))}</strong> —
  <a href="/{h(meta['_slug'])}/">{h(meta.get("title", ""))}</a>
  <span class="muted">({h(meta.get("publication_type", ""))}, {h(meta.get("publication_date", ""))})</span>
</li>
"""
        )

    body = f"""
<main class="container">
  <h1>{h(SITE_TITLE)}</h1>
  <p class="muted">Publication landing pages for {h(PUBLISHER_NAME)}.</p>

  <div class="grid">
    {''.join(cards)}
  </div>

  <section class="record-section">
    <h2>Latest records</h2>
    <ul class="latest-list">
      {''.join(latest_items)}
    </ul>
  </section>
</main>
"""
    return html_doc(SITE_TITLE, body)


def render_category_page(category: str, records: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())

    items = []
    for meta in records:
        items.append(
            f"""
<li>
  <strong>{h(meta.get("epinova_id", ""))}</strong> —
  <a href="/{h(meta['_slug'])}/">{h(meta.get("title", ""))}</a>
  <br>
  <span class="muted">{h(meta.get("publication_type", ""))} · {h(meta.get("publication_date", ""))}</span>
</li>
"""
        )

    body = f"""
<main class="container">
  <p><a href="/">← EPINOVA Publications</a></p>
  <h1>{h(label)}</h1>
  <p class="muted">{len(records)} publication{'s' if len(records) != 1 else ''}</p>

  <ul class="category-list">
    {''.join(items)}
  </ul>
</main>
"""
    return html_doc(f"{label} | {SITE_TITLE}", body)


def clean_output_dir() -> None:
    """
    Keep docs/ in place and overwrite generated files.
    This avoids Windows WinError 32 when docs/ is open, watched, or previewed.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    asset_dir = OUTPUT_DIR / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    copied = False

    for candidate in LOGO_CANDIDATES:
        source = ROOT / candidate
        if source.exists() and source.is_file():
            shutil.copy2(source, OUTPUT_DIR / OUTPUT_LOGO_PATH)
            copied = True
            print(f"Copied logo: {source}")
            break

    if not copied:
        print("Warning: no logo found. Expected one of:")
        for candidate in LOGO_CANDIDATES:
            print(f"  - {ROOT / candidate}")
        print("The page will still render, but the logo image may be missing.")


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    print(f"Repository root: {ROOT}")
    print(f"Output directory: {OUTPUT_DIR}")

    records = load_metadata_files()

    if not records:
        print("No metadata records found.")
        return

    clean_output_dir()
    copy_assets()

    for meta in records:
        copy_record_files(meta)

    for meta in records:
        slug = meta["_slug"]
        page_path = OUTPUT_DIR / slug / "index.html"
        write_page(page_path, render_record_page(meta))

    write_page(OUTPUT_DIR / "index.html", render_index_page(records))

    category_groups = defaultdict(list)
    for meta in records:
        category = meta.get("category", "uncategorized") or "uncategorized"
        category_groups[category].append(meta)

    for category, group_records in category_groups.items():
        category_page = OUTPUT_DIR / category / "index.html"
        write_page(category_page, render_category_page(category, group_records))

    print(f"Generated {len(records)} landing pages.")
    print(f"Site output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()