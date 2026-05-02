import json
import shutil
from pathlib import Path
from html import escape
from urllib.parse import quote
from datetime import date
from collections import defaultdict

# =========================================================
# EPINOVA Landing Page Generator
# Integrated version: metadata landing pages + archived Articles
#
# Reads:
# - all metadata.json files outside docs/ and Articles/
# - Articles/articles_archive_index.json
#
# Generates:
# - docs/index.html
# - docs/<category>/index.html
# - docs/<epinova-id-slug>/index.html for normal metadata records
# - docs/files/<slug>/<filename> for publication files
# - docs/articles/archive/<article-folder>/article.html for archived articles
#
# Article behavior:
# - Archived Articles do NOT receive Zenodo-like landing pages.
# - /articles/ lists Articles from Articles/articles_archive_index.json.
# - Each Article link points directly to its copied article.html.
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
    "assets/logo.jpg",
]
OUTPUT_LOGO_PATH = "assets/global-ai-governance-logo.png"

ARTICLE_ARCHIVE_SOURCE_DIR_NAME = "Articles"
ARTICLE_ARCHIVE_INDEX_NAME = "articles_archive_index.json"
ARTICLE_ARCHIVE_FAILED_INDEX_NAME = "articles_failed_index.json"
ARTICLE_ARCHIVE_OUTPUT_SUBDIR = "articles/archive"

CATEGORY_ORDER = [
    "articles",
    "policy-briefs",
    "working-papers",
    "white-books",
    "research-reports",
    "policy-reports",
]

CATEGORY_LABELS = {
    "articles": "Articles",
    "policy-briefs": "Policy Briefs",
    "working-papers": "Working Papers",
    "white-books": "White Books",
    "research-reports": "Research Reports",
    "policy-reports": "Policy Reports",
    "reports": "Reports",
    "other": "Other",
    "uncategorized": "Uncategorized",
}

HIDDEN_CATEGORIES = {"reports"}
SKIP_PARTS = {"docs", "site", "generated", ".git", "__pycache__"}

CREATOR = {
    "name": "Shaoyuan Wu",
    "affiliation": PUBLISHER_NAME,
    "orcid": "https://orcid.org/0009-0008-0660-8232",
}


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
    value = value.replace("–", "-").replace("—", "-").replace("−", "-")
    value = value.replace("_", "-").replace(" ", "-")
    value = value.replace(".", "-").replace("/", "-").replace("\\", "-")
    allowed = []
    for ch in value:
        if ch.isalnum() or ch == "-":
            allowed.append(ch)
    value = "".join(allowed)
    while "--" in value:
        value = value.replace("--", "-")
    return value.strip("-") or "untitled"


def get_slug(meta: dict) -> str:
    epinova_id = meta.get("epinova_id", "")
    if epinova_id:
        return normalize_slug(epinova_id)
    return normalize_slug(meta.get("title", ""))[:90] or "untitled"


def article_archive_index_path() -> Path:
    return ROOT / ARTICLE_ARCHIVE_SOURCE_DIR_NAME / ARTICLE_ARCHIVE_INDEX_NAME


def article_archive_source_dir() -> Path:
    return ROOT / ARTICLE_ARCHIVE_SOURCE_DIR_NAME


def article_archive_public_path(folder_name: str) -> str:
    return f"/{ARTICLE_ARCHIVE_OUTPUT_SUBDIR}/{quote(folder_name, safe='')}/article.html"


def record_href(meta: dict) -> str:
    if meta.get("_is_article_archive"):
        return meta.get("_direct_url", "") or article_archive_public_path(meta.get("_article_folder_name", ""))
    return f"/{h(meta.get('_slug', 'untitled'))}/"


def should_skip(metadata_path: Path) -> bool:
    if any(part in SKIP_PARTS for part in metadata_path.parts):
        return True
    try:
        rel = metadata_path.relative_to(ROOT)
        if rel.parts and rel.parts[0] == ARTICLE_ARCHIVE_SOURCE_DIR_NAME:
            # Articles are loaded from Articles/articles_archive_index.json.
            return True
    except ValueError:
        pass
    return False


def load_metadata_files() -> list[dict]:
    records = []
    for path in sorted(ROOT.rglob(METADATA_NAME)):
        if should_skip(path):
            continue
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Warning: failed to read {path}: {exc}")
            continue
        meta["_metadata_path"] = str(path.relative_to(ROOT))
        meta["_metadata_abs_path"] = str(path)
        meta["_slug"] = get_slug(meta)
        meta["_page_url"] = f"{SITE_BASE_URL}/{meta['_slug']}/"
        records.append(meta)
    records.sort(key=lambda r: (r.get("publication_date", ""), r.get("epinova_id", ""), r.get("title", "")), reverse=True)
    return records


def load_article_archive_records() -> list[dict]:
    index_path = article_archive_index_path()
    if not index_path.exists():
        print(f"Warning: article archive index not found: {index_path}")
        return []
    try:
        raw = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Warning: failed to read article archive index {index_path}: {exc}")
        return []
    if not isinstance(raw, list):
        print(f"Warning: article archive index is not a list: {index_path}")
        return []

    records = []
    seen_folders = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        if item.get("status") and item.get("status") != "archived":
            continue
        title = item.get("title") or item.get("expected_title") or "Untitled Article"
        publication_date = item.get("date") or item.get("publication_date") or ""
        folder_value = item.get("folder") or ""

        # Cloudflare builds on Linux, while articles_archive_index.json may
        # contain Windows absolute paths such as:
        # D:\...\EPINOVA-Research\Articles\2026-04-21_xxx
        # pathlib.Path(...).name does NOT treat backslashes as separators on Linux.
        # Therefore normalize backslashes before extracting the final folder name.
        if folder_value:
            folder_name = Path(str(folder_value).replace("\\", "/")).name
        else:
            folder_name = f"{publication_date}_{normalize_slug(title)[:80]}"

        if not folder_name:
            folder_name = normalize_slug(title)[:80] or "untitled-article"
        if folder_name in seen_folders:
            continue
        seen_folders.add(folder_name)

        direct_url = article_archive_public_path(folder_name)
        slug = f"article-{normalize_slug(folder_name)}"
        desc = item.get("description", "") or "Archived EPINOVA article preserved from the GoDaddy blog system."
        original_url = item.get("url", "")
        records.append({
            "epinova_id": "",
            "record_type": "Publication",
            "resource_type": "Text",
            "publication_type": "Article",
            "category": "articles",
            "title": title,
            "full_title": title,
            "subtitle": "",
            "publication_date": publication_date,
            "version": "v1.0",
            "language": "en",
            "status": "Archived",
            "visibility": "Public",
            "creators": [CREATOR],
            "publisher": PUBLISHER_NAME,
            "description": desc,
            "abstract": desc,
            "keywords": [],
            "subjects": ["AI governance", "Strategic systems analysis", "Technology policy"],
            "original_page": original_url,
            "official_page": original_url,
            "files": [{"filename": "article.html", "content_type": "text/html", "description": "Preserved HTML copy of the EPINOVA article."}],
            "_metadata_path": str(index_path.relative_to(ROOT)),
            "_metadata_abs_path": str(index_path),
            "_slug": slug,
            "_page_url": f"{SITE_BASE_URL}{direct_url}",
            "_is_article_archive": True,
            "_article_folder_name": folder_name,
            "_article_source_folder": folder_value,
            "_direct_url": direct_url,
        })
    records.sort(key=lambda r: (r.get("publication_date", ""), r.get("title", "")), reverse=True)
    print(f"Loaded archived articles: {len(records)} from {index_path}")
    return records


def copy_article_archive_files(article_records: list[dict]) -> None:
    if not article_records:
        return
    source_root = article_archive_source_dir()
    target_root = OUTPUT_DIR / ARTICLE_ARCHIVE_OUTPUT_SUBDIR
    target_root.mkdir(parents=True, exist_ok=True)

    index_path = article_archive_index_path()
    if index_path.exists():
        shutil.copy2(index_path, target_root / ARTICLE_ARCHIVE_INDEX_NAME)
    failed_index = source_root / ARTICLE_ARCHIVE_FAILED_INDEX_NAME
    if failed_index.exists():
        shutil.copy2(failed_index, target_root / ARTICLE_ARCHIVE_FAILED_INDEX_NAME)

    copied_count = 0

    for meta in article_records:
        folder_value = meta.get("_article_source_folder", "") or ""
        folder_name = meta.get("_article_folder_name", "") or ""

        # Cloudflare builds on Linux, so Windows absolute paths stored in
        # articles_archive_index.json cannot be used directly. Always reduce
        # the saved path to its final archive-folder name and then read from
        # repository-local Articles/<folder_name>.
        if folder_value:
            normalized_folder_value = folder_value.replace("\\", "/")
            folder_name = Path(normalized_folder_value).name

        if not folder_name:
            print(f"Warning: missing archived article folder name for: {meta.get('title', '')}")
            continue

        source_dir = source_root / folder_name
        target_dir = target_root / folder_name

        if not source_dir.exists() or not source_dir.is_dir():
            print(f"Warning: archived article folder not found: {source_dir}")
            continue

        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.copytree(
            source_dir,
            target_dir,
            ignore=shutil.ignore_patterns(".DS_Store", "Thumbs.db", "__pycache__"),
        )
        copied_count += 1

    print(f"Copied archived article folders: {copied_count}/{len(article_records)}")


def first_creator(meta: dict) -> str:
    creators = meta.get("creators", [])
    if isinstance(creators, list) and creators:
        first = creators[0]
        if isinstance(first, dict):
            return first.get("name", "")
        return str(first)
    return meta.get("author", "")


def all_creators_plain(meta: dict) -> list[str]:
    names = []
    creators = meta.get("creators", [])
    if isinstance(creators, list):
        for creator in creators:
            if isinstance(creator, dict):
                name = creator.get("name", "")
                if name:
                    names.append(name)
            elif creator:
                names.append(str(creator))
    return names


def local_file_url(meta: dict, filename: str, absolute: bool = False) -> str:
    slug = meta.get("_slug", "untitled")
    path = f"/files/{slug}/{quote(filename, safe='')}"
    return f"{SITE_BASE_URL}{path}" if absolute else path


def is_pdf_filename(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


def first_pdf_url(meta: dict) -> str:
    for item in meta.get("files", []) if isinstance(meta.get("files", []), list) else []:
        if isinstance(item, dict):
            fn = item.get("filename", "")
            if fn and is_pdf_filename(fn):
                return local_file_url(meta, fn, absolute=True)
    return ""


def copy_record_files(meta: dict) -> None:
    metadata_abs_path = meta.get("_metadata_abs_path")
    if not metadata_abs_path:
        return
    source_dir = Path(metadata_abs_path).parent
    target_dir = OUTPUT_DIR / "files" / meta.get("_slug", "untitled")
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
        target_file.parent.mkdir(parents=True, exist_ok=True)
        if source_file.exists() and source_file.is_file():
            shutil.copy2(source_file, target_file)
        else:
            print(f"Warning: source file not found: {source_file}")


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
            line.append(f"<br><a href='{h(orcid)}'>{h(orcid)}</a>" if str(orcid).startswith("http") else f"<br><span class='muted'>{h(orcid)}</span>")
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
                label = item.get("title") or item.get("name") or item.get("identifier") or str(item)
                items.append(f"<li>{h(label)}</li>")
            else:
                items.append(f"<li>{h(item)}</li>")
        return "<ul>" + "\n".join(items) + "</ul>"
    return f"<p>{h(values)}</p>"


def references_html(meta: dict) -> str:
    refs = meta.get("references", [])
    if not refs:
        return "<p class='muted'>No references listed.</p>"
    return "<ol class='references'>" + "\n".join(f"<li>{linkify_urls(h(ref))}</li>" for ref in refs) + "</ol>"


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
        if str(identifier).startswith("http"):
            identifier_html = f"<a href='{h(identifier)}'>{h(identifier)}</a>"
        elif str(scheme).upper() == "DOI":
            identifier_html = f"<a href='https://doi.org/{h(identifier)}'>{h(identifier)}</a>"
        else:
            identifier_html = h(identifier)
        rows.append(f"<tr><td>{h(scheme)}</td><td>{identifier_html}</td><td>{h(description)}</td></tr>")
    return "<table><thead><tr><th>Scheme</th><th>Identifier</th><th>Description</th></tr></thead><tbody>" + "\n".join(rows) + "</tbody></table>"


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
        if str(identifier).startswith("http"):
            identifier_html = f"<a href='{h(identifier)}'>{h(identifier)}</a>"
        elif str(scheme).upper() == "DOI":
            identifier_html = f"<a href='https://doi.org/{h(identifier)}'>{h(identifier)}</a>"
        else:
            identifier_html = h(identifier)
        rows.append(f"<tr><td>{h(relation)}</td><td>{identifier_html}</td><td>{h(resource_type)}</td><td>{h(description)}</td></tr>")
    return "<table><thead><tr><th>Relation</th><th>Identifier</th><th>Type</th><th>Description</th></tr></thead><tbody>" + "\n".join(rows) + "</tbody></table>"


def file_preview_html(meta: dict) -> str:
    files = meta.get("files", [])
    if not isinstance(files, list) or not files:
        return """
<section class="record-section"><h2>Files</h2><p class="muted">No files listed.</p></section>
"""
    preview = ""
    for item in files:
        if isinstance(item, dict) and is_pdf_filename(item.get("filename", "")):
            filename = item.get("filename", "")
            preview_url = local_file_url(meta, filename)
            preview = f"""
<div class="file-preview">
  <div class="file-preview-title">PDF preview</div>
  <iframe src="{h(preview_url)}" title="{h(filename)}"></iframe>
</div>
"""
            break
    rows = []
    for file_entry in files:
        if not isinstance(file_entry, dict):
            continue
        fn = file_entry.get("filename", "File")
        file_type = file_entry.get("content_type", "")
        desc = file_entry.get("description", "")
        download_url = local_file_url(meta, fn) if fn else ""
        name_html = f"<a href='{h(download_url)}'>{h(fn)}</a>" if fn else ""
        action_html = f"<a class='button small' href='{h(download_url)}'>Download</a>" if fn else ""
        rows.append(f"<tr><td>{name_html}<br><span class='muted'>{h(desc)}</span></td><td>{h(file_type)}</td><td class='right'>{action_html}</td></tr>")
    return f"""
<section class="record-section">
  <h2>Files</h2>
  {preview}
  <div class="panel">
    <div class="panel-heading">Files</div>
    <table class="file-table"><thead><tr><th>Name</th><th>Type</th><th></th></tr></thead><tbody>{''.join(rows)}</tbody></table>
  </div>
</section>
"""


def sidebar_details_html(meta: dict) -> str:
    doi = meta_value(meta, "doi", "")
    previous_doi = meta_value(meta, "previous_doi", "")
    doi_html = f"<a href='{h(doi)}'>{h(doi)}</a>" if doi.startswith("http") else h(doi)
    previous_doi_html = f"<dt>Previous DOI</dt><dd><a href='https://doi.org/{h(previous_doi)}'>{h(previous_doi)}</a></dd>" if previous_doi else ""
    return f"""
<div class="sidebar-box">
  <h2>Details</h2>
  <dl class="details-list">
    <dt>DOI</dt><dd>{doi_html}</dd>
    {previous_doi_html}
    <dt>EPINOVA ID</dt><dd>{h(meta_value(meta, 'epinova_id', ''))}</dd>
    <dt>Resource type</dt><dd>{h(meta_value(meta, 'resource_type', ''))}</dd>
    <dt>Publication type</dt><dd>{h(meta_value(meta, 'publication_type', ''))}</dd>
    <dt>Publication date</dt><dd>{h(meta_value(meta, 'publication_date', ''))}</dd>
    <dt>Version</dt><dd>{h(meta_value(meta, 'version', ''))}</dd>
    <dt>Status</dt><dd>{h(meta_value(meta, 'status', ''))}</dd>
    <dt>Language</dt><dd>{h(meta_value(meta, 'language', ''))}</dd>
    <dt>Publisher</dt><dd>{h(meta_value(meta, 'publisher', ''))}</dd>
    <dt>Place</dt><dd>{h(meta_value(meta, 'place', ''))}</dd>
  </dl>
</div>
"""


def sidebar_rights_html(meta: dict) -> str:
    license_data = meta.get("license", {})
    if isinstance(license_data, dict):
        license_title = license_data.get("title", "") or license_data.get("name", "")
        license_url = license_data.get("url", "")
    else:
        license_title = str(license_data)
        license_url = ""
    license_html = f"<a href='{h(license_url)}'>{h(license_title)}</a>" if license_url else h(license_title or "Not specified")
    return f"""
<div class="sidebar-box">
  <h2>Rights</h2>
  <dl class="details-list"><dt>License</dt><dd>{license_html}</dd><dt>Copyright</dt><dd>{h(meta_value(meta, 'copyright', ''))}</dd></dl>
</div>
"""


def sidebar_citation_html(meta: dict) -> str:
    citation = meta_value(meta, "citation_apa", "") or meta_value(meta, "recommended_citation", "")
    return f"<div class='sidebar-box'><h2>Citation</h2><p class='citation-text'>{h(citation)}</p></div>"


def sidebar_export_html(meta: dict) -> str:
    items = []
    repository_folder = meta_value(meta, "repository_folder", "")
    official_page = meta_value(meta, "official_page", "")
    metadata_path = meta.get("_metadata_path", "")
    if repository_folder:
        items.append(f"<li><a href='{h(repository_folder)}'>Repository folder</a></li>")
    if official_page:
        items.append(f"<li><a href='{h(official_page)}'>Official EPINOVA page</a></li>")
    if metadata_path:
        items.append(f"<li><span class='muted'>Metadata path:</span><br>{h(metadata_path)}</li>")
    if not items:
        items.append("<li class='muted'>No export links listed.</li>")
    return f"<div class='sidebar-box'><h2>Export</h2><ul class='sidebar-links'>{''.join(items)}</ul></div>"


def page_css() -> str:
    return """
:root { --text:#202020; --muted:#666; --border:#d9d9d9; --soft:#f7f7f7; --link:#0b5cad; --dark:#050505; --green:#2f7d32; }
* { box-sizing: border-box; }
body { margin:0; font-family: Arial, Helvetica, sans-serif; color:var(--text); background:#fff; line-height:1.55; }
a { color:var(--link); overflow-wrap:anywhere; text-decoration:none; }
a:hover { text-decoration:underline; }
.topbar { background:var(--dark); color:#fff; border-bottom:1px solid #222; }
.topbar-inner { max-width:1180px; min-height:160px; margin:0 auto; padding:12px 24px; display:flex; align-items:center; justify-content:center; }
.brand-logo-wrap { width:620px; height:100px; overflow:hidden; display:flex; align-items:center; justify-content:center; }
.brand-logo { width:560px; height:auto; object-fit:contain; display:block; transform:translateX(-18px) scale(1.05); transform-origin:center center; }
.publication-nav-bar { width:100%; background:#f4f4f4; border-top:1px solid #d6d6d6; border-bottom:1px solid #d6d6d6; }
.publication-nav { max-width:1180px; margin:0 auto; padding:11px 24px; display:flex; align-items:center; justify-content:center; gap:34px; flex-wrap:wrap; }
.publication-nav a { color:#222; font-size:13px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }
.container { max-width:1180px; margin:0 auto; padding:32px 24px 48px; }
.record-grid { display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:34px; align-items:start; }
.record-info-row { display:flex; justify-content:space-between; gap:18px; align-items:center; margin-bottom:20px; color:var(--muted); font-size:14px; }
.label-group { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.label { display:inline-flex; border:1px solid var(--border); background:#f1f1f1; border-radius:4px; padding:4px 8px; font-size:12px; color:#333; }
.label-open { color:var(--green); border-color:#b6d7b9; background:#f5fbf5; }
h1 { font-size:34px; line-height:1.22; margin:0 0 16px; font-weight:700; }
h2 { font-size:22px; line-height:1.3; margin:32px 0 12px; }
h3 { font-size:17px; margin:0 0 10px; }
.record-section { margin-top:28px; }
.plain-list { padding-left:20px; }
.muted { color:var(--muted); }
.panel, .file-preview, .sidebar-box { border:1px solid var(--border); border-radius:4px; background:#fff; overflow:hidden; margin-top:14px; }
.panel-heading, .file-preview-title, .sidebar-box h2 { background:var(--soft); border-bottom:1px solid var(--border); padding:10px 14px; font-weight:700; }
.file-preview iframe { width:100%; height:620px; border:0; background:#eee; }
table { width:100%; border-collapse:collapse; font-size:14px; }
th, td { border-top:1px solid var(--border); padding:9px 10px; text-align:left; vertical-align:top; }
thead th { background:var(--soft); border-top:0; }
.file-table td.right { text-align:right; white-space:nowrap; }
.button { display:inline-block; border:1px solid #777; border-radius:4px; padding:7px 11px; color:#111; background:#fff; }
.button.small { padding:4px 8px; font-size:13px; }
.sidebar-box { margin-bottom:18px; }
.sidebar-box h2 { margin:0; font-size:17px; }
.details-list { margin:0; padding:14px; }
.details-list dt { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; margin-top:12px; font-weight:700; }
.details-list dt:first-child { margin-top:0; }
.details-list dd { margin:4px 0 0; overflow-wrap:anywhere; }
.sidebar-links { margin:0; padding:14px 14px 14px 32px; }
.citation-text { margin:0; padding:14px; font-size:14px; overflow-wrap:anywhere; }
.references li, .latest-list li, .category-list li { margin-bottom:10px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin-top:24px; }
.card { display:block; border:1px solid var(--border); border-radius:6px; padding:18px; color:var(--text); background:#fff; }
.latest-category-block, .year-block { margin-top:22px; }
.subcategory-block { margin-top:34px; }
.subcategory-block h2 { font-size:21px; margin:0 0 16px; padding-bottom:6px; border-bottom:1px solid var(--border); }
.footer { background:var(--dark); color:#ccc; margin-top:48px; }
.footer-inner { max-width:1180px; margin:0 auto; padding:28px 24px; display:grid; grid-template-columns:1.5fr 1fr 1fr; gap:24px; font-size:14px; }
.footer h2 { color:#fff; margin:0 0 10px; font-size:14px; text-transform:uppercase; letter-spacing:.08em; }
.footer a { color:#fff; }
.footer-bottom { border-top:1px solid #222; padding-top:14px; margin-top:14px; grid-column:1 / -1; color:#aaa; font-size:13px; }
@media (max-width:900px){ .record-grid{grid-template-columns:1fr;} .topbar-inner{min-height:116px;} .brand-logo-wrap{width:660px;height:96px;overflow:visible;} .brand-logo{width:600px;max-height:86px;transform:translateX(-18px);} h1{font-size:28px;} .file-preview iframe{height:460px;} .footer-inner{grid-template-columns:1fr;} }
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
    citation_authors = "\n".join(f'  <meta name="citation_author" content="{h(name)}">' for name in all_creators_plain(meta))
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
  <meta name="citation_publication_date" content="{h(meta.get('publication_date', ''))}">
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
    creators = [{"@type": "Person", "name": name} for name in all_creators_plain(meta)]
    identifier = meta.get("doi", "")
    if identifier and not identifier.startswith("http") and not identifier.startswith("To be assigned"):
        identifier = f"https://doi.org/{identifier}"
    if identifier.startswith("To be assigned"):
        identifier = meta.get("_page_url", "")
    data = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle" if meta.get("category") != "articles" else "Article",
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
        "publisher": {"@type": "Organization", "name": meta.get("publisher", PUBLISHER_NAME)},
    }
    license_data = meta.get("license", {})
    if isinstance(license_data, dict) and license_data.get("url"):
        data["license"] = license_data.get("url")
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def site_header() -> str:
    return f"""
<header class="topbar">
  <div class="topbar-inner logo-only-header">
    <div class="brand-logo-wrap"><img class="brand-logo" src="/{h(OUTPUT_LOGO_PATH)}" alt="Global AI Governance and Policy Research Center, EPINOVA LLC"></div>
  </div>
</header>
<div class="publication-nav-bar">
  <nav class="publication-nav" aria-label="Publication navigation">
    <a href="/">Publications</a>
    <a href="/articles/">Articles</a>
    <a href="/policy-briefs/">Policy Briefs</a>
    <a href="/working-papers/">Working Papers</a>
    <a href="/white-books/">White Books</a>
    <a href="/research-reports/">Research Reports</a>
    <a href="{h(EPINOVA_MAIN_SITE)}">EPINOVA</a>
  </nav>
</div>
"""


def site_footer() -> str:
    return f"""
<footer class="footer">
  <div class="footer-inner">
    <div><h2>About</h2><p>{h(CENTER_NAME)} publishes structured open-access research outputs through EPINOVA LLC.</p></div>
    <div><h2>Publications</h2><p><a href="/">Publication index</a><br><a href="/articles/">Articles</a><br><a href="/policy-briefs/">Policy Briefs</a><br><a href="/working-papers/">Working Papers</a><br><a href="/white-books/">White Books</a></p></div>
    <div><h2>Links</h2><p><a href="{h(EPINOVA_MAIN_SITE)}">EPINOVA main site</a><br><a href="https://github.com/EPINOVALLC/EPINOVA-Research">GitHub repository</a></p></div>
    <div class="footer-bottom">Generated on {date.today().isoformat()} from EPINOVA metadata records and archived Articles.</div>
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
    description = meta_value(meta, "description", "")
    abstract = meta_value(meta, "abstract", "")
    recommended_citation = meta_value(meta, "recommended_citation", "")
    citation_apa = meta_value(meta, "citation_apa", "")
    body = f"""
<main class="container">
  <div class="record-grid">
    <article class="record-main">
      <section class="record-info-row"><div><span>Published {h(publication_date)}</span><span class="muted"> | Version {h(version)}</span></div><div class="label-group"><span class="label">{h(publication_type)}</span><span class="label label-open">Open</span><span class="label">{h(status)}</span></div></section>
      <section><h1>{h(title)}</h1><div class="creators">{creators_html(meta)}</div></section>
      <section class="record-section rich-text"><h2>Description</h2><p>{h(description)}</p></section>
      <section class="record-section rich-text"><h2>Abstract</h2><p>{h(abstract)}</p></section>
      {file_preview_html(meta)}
      <section class="record-section"><h2>Keywords</h2>{list_html(meta.get('keywords', []))}</section>
      <section class="record-section"><h2>Subjects</h2>{list_html(meta.get('subjects', []))}</section>
      <section class="record-section"><h2>Recommended citation</h2><p>{h(recommended_citation)}</p></section>
      <section class="record-section"><h2>APA citation</h2><p>{h(citation_apa)}</p></section>
      <section class="record-section"><h2>Alternate identifiers</h2>{alternate_ids_html(meta)}</section>
      <section class="record-section"><h2>Related works</h2>{related_works_html(meta)}</section>
      <section class="record-section"><h2>References</h2>{references_html(meta)}</section>
    </article>
    <aside class="record-sidebar">{sidebar_details_html(meta)}{sidebar_rights_html(meta)}{sidebar_citation_html(meta)}{sidebar_export_html(meta)}</aside>
  </div>
</main>
"""
    return html_doc(f"{title} | {SITE_TITLE}", body, meta)


def publication_year(meta: dict) -> str:
    publication_date = meta.get("publication_date", "") or ""
    if len(publication_date) >= 4 and publication_date[:4].isdigit():
        return publication_date[:4]
    return "Undated"


def full_display_title(meta: dict) -> str:
    full_title = meta.get("full_title", "") or meta.get("title_full", "")
    if full_title:
        return full_title
    title = meta.get("title", "") or ""
    subtitle = meta.get("subtitle", "") or ""
    return f"{title}: {subtitle}" if title and subtitle else title


def working_paper_subcategory(meta: dict) -> tuple[str, str]:
    epinova_id = meta.get("epinova_id", "") or ""
    subgroup_labels = {
        "A": "AI-Strategic Nodes and Structural Governance",
        "B": "AI Governance and Institutional Systems",
        "C": "Compute Infrastructure and Data-Center Governance",
        "D": "Domestic Governance, Infrastructure, and Policy Friction",
        "E": "AI Economy, Firms, and Organizational Transformation",
        "F": "Networked Conflict, Security, and Strategic Systems",
        "G": "Maritime, Arctic, and Geostrategic Systems",
    }
    legacy_subgroup_map = {"EPINOVA-WP-2025-001": "F"}
    if epinova_id in legacy_subgroup_map:
        code = legacy_subgroup_map[epinova_id]
        return code, subgroup_labels.get(code, f"Working Paper Series {code}")
    parts = epinova_id.split("-")
    if len(parts) >= 5 and parts[1] == "WP":
        code = parts[2]
        return code, subgroup_labels.get(code, f"Working Paper Series {code}")
    return "Z", "Other Working Papers"


def render_index_page(records: list[dict]) -> str:
    category_counts = defaultdict(int)
    for meta in records:
        category = meta.get("category", "uncategorized") or "uncategorized"
        if category not in HIDDEN_CATEGORIES:
            category_counts[category] += 1

    cards = []
    for category in CATEGORY_ORDER:
        if category in HIDDEN_CATEGORIES:
            continue
        label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())
        count = category_counts.get(category, 0)
        cards.append(f"<a class='card' href='/{h(category)}/'><h2>{h(label)}</h2><p>{count} publication{'s' if count != 1 else ''}</p></a>")
    for category in sorted(category_counts.keys()):
        if category in CATEGORY_ORDER or category in HIDDEN_CATEGORIES:
            continue
        label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())
        count = category_counts.get(category, 0)
        cards.append(f"<a class='card' href='/{h(category)}/'><h2>{h(label)}</h2><p>{count} publication{'s' if count != 1 else ''}</p></a>")

    latest_category_order = [
        ("articles", "A. Articles"),
        ("policy-briefs", "B. Policy Briefs"),
        ("working-papers", "C. Working Papers"),
        ("white-books", "D. White Books"),
        ("policy-reports", "E. Policy Reports"),
        ("research-reports", "F. Research Reports"),
    ]
    records_by_category = defaultdict(list)
    for meta in records:
        category = meta.get("category", "uncategorized") or "uncategorized"
        if category not in HIDDEN_CATEGORIES:
            records_by_category[category].append(meta)
    latest_sections = []
    for category, label in latest_category_order:
        group = records_by_category.get(category, [])
        if not group:
            continue
        group = sorted(group, key=lambda r: (r.get("publication_date", ""), r.get("epinova_id", ""), r.get("title", "")), reverse=True)
        items = []
        for meta in group[:5]:
            epinova_id = meta.get("epinova_id", "")
            title = full_display_title(meta)
            publication_type = meta.get("publication_type", "")
            publication_date = meta.get("publication_date", "")
            id_html = f"<strong>{h(epinova_id)}</strong> — " if epinova_id else ""
            detail = " · ".join(x for x in [publication_type, publication_date] if x)
            detail_html = f" <span class='muted'>({h(detail)})</span>" if detail else ""
            items.append(f"<li>{id_html}<a href='{h(record_href(meta))}'>{h(title)}</a>{detail_html}</li>")
        latest_sections.append(f"<section class='latest-category-block'><h3>{h(label)}</h3><ul class='latest-list'>{''.join(items)}</ul></section>")

    body = f"""
<main class="container">
  <h1>{h(SITE_TITLE)}</h1>
  <p class="muted">Publication landing pages for {h(PUBLISHER_NAME)}.</p>
  <div class="grid">{''.join(cards)}</div>
  <section class="record-section"><h2>Latest records</h2>{''.join(latest_sections)}</section>
</main>
"""
    return html_doc(SITE_TITLE, body)


def render_category_page(category: str, records: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category.replace("-", " ").title())

    if category == "working-papers":
        subgrouped = defaultdict(lambda: defaultdict(list))
        for meta in records:
            subgroup_code, subgroup_label = working_paper_subcategory(meta)
            subgrouped[(subgroup_code, subgroup_label)][publication_year(meta)].append(meta)
        sections = []
        for subgroup_code, subgroup_label in sorted(subgrouped.keys(), key=lambda x: x[0]):
            year_groups = subgrouped[(subgroup_code, subgroup_label)]
            year_sections = []
            for year in sorted(year_groups.keys(), reverse=True):
                group_records = sorted(year_groups[year], key=lambda r: (r.get("publication_date", ""), r.get("epinova_id", ""), r.get("title", "")), reverse=True)
                items = []
                for meta in group_records:
                    title = full_display_title(meta)
                    id_html = f"<strong>{h(meta.get('epinova_id', ''))}</strong> — " if meta.get("epinova_id") else ""
                    items.append(f"<li>{id_html}<a href='{h(record_href(meta))}'>{h(title)}</a><br><span class='muted'>{h(meta.get('publication_type', ''))} · {h(meta.get('publication_date', ''))}</span></li>")
                year_sections.append(f"<div class='year-block'><h3>{h(year)}</h3><ul class='category-list'>{''.join(items)}</ul></div>")
            sections.append(f"<section class='subcategory-block'><h2>{h(subgroup_code)}. {h(subgroup_label)}</h2>{''.join(year_sections)}</section>")
        body = f"<main class='container'><p><a href='/'>← EPINOVA Publications</a></p><h1>{h(label)}</h1><p class='muted'>{len(records)} publication{'s' if len(records) != 1 else ''}</p>{''.join(sections)}</main>"
        return html_doc(f"{label} | {SITE_TITLE}", body)

    if category in {"articles", "policy-briefs", "white-books", "research-reports", "policy-reports"}:
        records_by_year = defaultdict(list)
        for meta in records:
            records_by_year[publication_year(meta)].append(meta)
        year_sections = []
        for year in sorted(records_by_year.keys(), reverse=True):
            group_records = sorted(records_by_year[year], key=lambda r: (r.get("publication_date", ""), r.get("epinova_id", ""), r.get("title", "")), reverse=True)
            items = []
            for meta in group_records:
                title = full_display_title(meta)
                id_html = f"<strong>{h(meta.get('epinova_id', ''))}</strong> — " if meta.get("epinova_id") else ""
                original = meta.get("original_page") or meta.get("official_page") or ""
                original_html = f" <span class='muted'>· <a href='{h(original)}'>Original</a></span>" if category == "articles" and original else ""
                items.append(f"<li>{id_html}<a href='{h(record_href(meta))}'>{h(title)}</a>{original_html}<br><span class='muted'>{h(meta.get('publication_type', ''))} · {h(meta.get('publication_date', ''))}</span></li>")
            year_sections.append(f"<div class='year-block'><h2>{h(year)}</h2><ul class='category-list'>{''.join(items)}</ul></div>")
        body = f"<main class='container'><p><a href='/'>← EPINOVA Publications</a></p><h1>{h(label)}</h1><p class='muted'>{len(records)} publication{'s' if len(records) != 1 else ''}</p>{''.join(year_sections)}</main>"
        return html_doc(f"{label} | {SITE_TITLE}", body)

    items = []
    for meta in records:
        title = full_display_title(meta)
        id_html = f"<strong>{h(meta.get('epinova_id', ''))}</strong> — " if meta.get("epinova_id") else ""
        items.append(f"<li>{id_html}<a href='{h(record_href(meta))}'>{h(title)}</a><br><span class='muted'>{h(meta.get('publication_type', ''))} · {h(meta.get('publication_date', ''))}</span></li>")
    body = f"<main class='container'><p><a href='/'>← EPINOVA Publications</a></p><h1>{h(label)}</h1><p class='muted'>{len(records)} publication{'s' if len(records) != 1 else ''}</p><ul class='category-list'>{''.join(items)}</ul></main>"
    return html_doc(f"{label} | {SITE_TITLE}", body)


def clean_output_dir() -> None:
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


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    print(f"Repository root: {ROOT}")
    print(f"Output directory: {OUTPUT_DIR}")

    publication_records = load_metadata_files()
    article_records = load_article_archive_records()
    records = publication_records + article_records

    if not records:
        print("No metadata records or archived Articles found.")
        return

    clean_output_dir()
    copy_assets()

    for meta in publication_records:
        copy_record_files(meta)

    copy_article_archive_files(article_records)

    for meta in publication_records:
        slug = meta["_slug"]
        write_page(OUTPUT_DIR / slug / "index.html", render_record_page(meta))

    write_page(OUTPUT_DIR / "index.html", render_index_page(records))

    category_groups = defaultdict(list)
    for meta in records:
        category = meta.get("category", "uncategorized") or "uncategorized"
        category_groups[category].append(meta)

    for category, group_records in category_groups.items():
        if category in HIDDEN_CATEGORIES:
            continue
        write_page(OUTPUT_DIR / category / "index.html", render_category_page(category, group_records))

    print(f"Generated {len(publication_records)} landing pages.")
    print(f"Linked {len(article_records)} archived Articles directly to article.html.")
    print(f"Site output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
