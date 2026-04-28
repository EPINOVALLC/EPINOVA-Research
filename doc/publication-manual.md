# EPINOVA Publication Manual v1.1

Global AI Governance and Policy Research Center  
EPINOVA LLC

---

## 1. Overview

EPINOVA adopts a standardized publication system to ensure consistency, traceability, interoperability, and long-term accessibility across its research outputs.

The system defines:

- Publication types
- Thematic series
- Publication identifiers
- Metadata structure
- Citation format
- DOI and landing-page workflow
- Repository and archival structure

This manual applies to research outputs published by EPINOVA LLC through its institutional publication infrastructure, including the EPINOVA website, the EPINOVA Publications site, GitHub repository records, and DOI metadata registration systems.

---

## 2. Publication Types

EPINOVA publications are organized into five primary publication types.

| Type | Code | Description |
|---|---:|---|
| Article | A | Short- and medium-form research articles on AI governance, technology, society, and interdisciplinary policy issues. |
| Working Paper | WP | Preliminary or developing research outputs released for scholarly discussion, methodological development, and policy analysis. |
| Report | R | Extended analytical reports, research assessments, empirical findings, methodological documentation, and structured policy evaluations. |
| Policy Brief | PB | Concise, evidence-based policy analysis for decision-makers, researchers, and public audiences. |
| White Book | WB / IWB | Comprehensive white books presenting institutional frameworks, indicator systems, long-form research, and strategic policy architectures. |

Notes:

- `IWB` may be used for major institutional white books or index-based white books.
- `WB` may be used for general white books.
- The publication type used in `metadata.json` should match the public-facing category used on `publications.epinova.org`.

---

## 3. Working Paper Series

Working Papers may be organized into thematic series.

| Series | Code | Scope |
|---|---:|---|
| Conflict & Strategic Dynamics | WP-F | Warfare, escalation, deterrence, strategic systems, systemic risk, and conflict modeling. |
| Digital Infrastructure & Data Governance | WP-D | Data centers, compute geography, digital infrastructure, data governance, and platform systems. |
| AI Governance & System Design | WP-A | AI governance models, system design, algorithmic structures, policy frameworks, and institutional architectures. |
| Governance & Institutions | WP-G | Institutional design, regulatory systems, governance theory, and public administration. |
| Economic Systems & AI | WP-E | AI economy, industrial transformation, productivity, labor markets, and economic systems. |
| Security Systems | WP-S | Infrastructure security, cyber-physical systems, adversarial systems, and strategic security analysis. |

Notes:

- Series codes are used mainly for Working Papers.
- Other publication types may omit the thematic series unless an internal project requires it.

---

## 4. Publication Identifier Structure

All EPINOVA publications use a standardized identifier.

### 4.1 General Structure

```text
EPINOVA-[TYPE]-[YEAR]-[NUMBER]
```

Examples:

```text
EPINOVA-PB-2026-041
EPINOVA-R-2026-003
EPINOVA-A-2026-002
EPINOVA-WB-2026-001
EPINOVA-IWB-2026-001
```

### 4.2 Working Paper Structure

Working Papers may include a series code:

```text
EPINOVA-WP-[SERIES]-[YEAR]-[NUMBER]
```

Examples:

```text
EPINOVA-WP-F-2026-009
EPINOVA-WP-A-2026-002
EPINOVA-WP-D-2026-001
```

### 4.3 Formatting Rules

- Use standard hyphens `-` in machine-readable identifiers.
- Avoid using en dash `–` or em dash `—` in identifiers used for filenames, metadata, URLs, DOI suffixes, and repository paths.
- Display titles may use typographic dashes where appropriate, but identifiers should remain machine-stable.
- The annual number resets within each publication type or series.
- Recommended number padding is three digits: `001`, `009`, `041`.

---

## 5. DOI Suffix Structure

After EPINOVA receives its Crossref DOI prefix, DOI suffixes should be generated from EPINOVA identifiers.

### 5.1 Recommended DOI Suffix Format

```text
epinova.[type].[year].[number]
epinova.wp.[series].[year].[number]
```

Examples:

```text
epinova.pb.2026.041
epinova.r.2026.003
epinova.wb.2026.001
epinova.wp.f.2026.009
```

### 5.2 Pending DOI Statement

Before Crossref membership and DOI prefix approval, DOI fields should use:

```text
DOI: To be assigned after Crossref membership approval.
```

In `metadata.json`, the `doi` field should use:

```json
"doi": "To be assigned after Crossref membership approval"
```

In citation fields, use:

```text
DOI: To be assigned after Crossref membership approval.
```

---

## 6. Citation Format

### 6.1 Recommended Citation

EPINOVA uses an APA-style institutional citation format.

```text
Author. (Year). Title. EPINOVA [Publication Type] Series, [EPINOVA Identifier]. Global AI Governance and Policy Research Center, EPINOVA LLC. DOI or URL.
```

Example with existing Zenodo DOI:

```text
Wu, Shaoyuan. (2026). A Systemic Theory of Escalation and the Loss-of-Control Threshold in Networked Conflict. EPINOVA Working Paper Series, EPINOVA-WP-F-2026-009. Global AI Governance and Policy Research Center, EPINOVA LLC. https://doi.org/10.5281/zenodo.19139977
```

Example with pending Crossref DOI:

```text
Wu, Shaoyuan. (2026). Energy Endurance Under Systemic Shock: Divergent Survival Pathways in East Asia During the U.S.–Israel–Iran Conflict. EPINOVA Policy Brief Series, EPINOVA-PB-2026-041. Global AI Governance and Policy Research Center, EPINOVA LLC. DOI: To be assigned after Crossref membership approval.
```

### 6.2 Metadata Citation Fields

Each publication metadata record should include:

```json
"recommended_citation": "...",
"citation_apa": "..."
```

Both fields should remain consistent unless a specific citation style requires variation.

---

## 7. Author Name Standardization

All individual publications should use a consistent author name format.

```text
Wu, Shaoyuan
```

Recommended creator metadata:

```json
{
  "name": "Wu, Shaoyuan",
  "given_name": "Shaoyuan",
  "family_name": "Wu",
  "affiliation": "Global AI Governance and Policy Research Center, EPINOVA LLC",
  "orcid": "https://orcid.org/0009-0008-0660-8232"
}
```

Notes:

- Do not use inconsistent variations such as `Wu Shao-Yuan`, `S. Wu`, or `Shaoyuan Wu` in citation fields.
- In institutional outputs, EPINOVA LLC or the Global AI Governance and Policy Research Center may appear as publisher, contributor, or institutional author where appropriate.

---

## 8. Versioning

EPINOVA publications may include version numbers.

| Version | Meaning |
|---|---|
| v0.1 | Draft, concept note, or initial working version |
| v1.0 | Stable first public release |
| v1.1 / v1.2 | Minor revisions, metadata correction, formatting improvement, or limited content update |
| v2.0+ | Major revision, expanded edition, or substantive restructuring |

Example:

```text
AI Strategic Node Framework (v1.0)
```

Version information should be included in `metadata.json`:

```json
"version": "v1.0"
```

---

## 9. Metadata Structure

Each publication folder should contain at least:

```text
Publication Folder/
├── publication.pdf
└── metadata.json
```

Recommended repository structure:

```text
EPINOVA-Research/
├── Articles/
├── Policy Brief/
├── Working Paper/
├── Reports/
├── Index White Book/
├── assets/
├── tools/
└── docs/
```

Each `metadata.json` should include the following core fields:

```json
{
  "title": "",
  "epinova_id": "",
  "publication_type": "",
  "resource_type": "",
  "publication_date": "",
  "version": "",
  "status": "",
  "language": "en",
  "publisher": "Global AI Governance and Policy Research Center, EPINOVA LLC",
  "place": "United States",
  "doi": "To be assigned after Crossref membership approval",
  "previous_doi": "",
  "creators": [],
  "abstract": "",
  "description": "",
  "keywords": [],
  "subjects": [],
  "files": [],
  "license": {},
  "references": [],
  "recommended_citation": "",
  "citation_apa": "",
  "repository_url": "https://github.com/EPINOVALLC/EPINOVA-Research",
  "repository_folder": "",
  "landing_page": "",
  "crossref": {}
}
```

---

## 10. DOI and Archiving

EPINOVA publications may be assigned persistent identifiers through Crossref, Zenodo, DataCite-based repositories, or other recognized DOI registration infrastructures, depending on publication type and archival requirements.

### 10.1 Crossref

Crossref DOI registration is intended for EPINOVA-published:

- Articles
- Working Papers
- Reports
- Policy Briefs
- White Books
- Methodology notes

The Crossref DOI should resolve to the corresponding landing page on:

```text
https://publications.epinova.org/
```

### 10.2 Zenodo and Previous DOIs

Some EPINOVA research outputs may have been previously archived through Zenodo and assigned Zenodo DOIs. These should not be deleted or replaced silently.

For migrated records:

- The new EPINOVA Crossref DOI should be the primary DOI after registration.
- The previous Zenodo DOI should be retained as `previous_doi` or `alternate_identifiers`.
- The publication landing page should clearly show the previous DOI where relevant.

Example:

```json
"previous_doi": "10.5281/zenodo.19770272"
```

### 10.3 DataCite-Based Repositories

DataCite-based DOI services may be used for:

- Datasets
- Software
- Figures
- Supplementary research materials
- Replication packages
- Extended appendices

### 10.4 GitHub Repository

GitHub serves as the structural repository and version-control layer.

```text
https://github.com/EPINOVALLC/EPINOVA-Research
```

GitHub should preserve:

- PDF files
- `metadata.json`
- Landing-page generator scripts
- Publication source records
- Supplemental files

### 10.5 Institutional Portals

| Platform | Function |
|---|---|
| `epinova.org` | Institutional research portal and public-facing organizational website |
| `publications.epinova.org` | DOI landing pages and publication interface |
| GitHub | Repository, metadata, version control, and source publication records |
| Crossref | DOI and metadata registration for EPINOVA publications |
| DataCite-based repositories / OSF / Figshare / Dataverse | Datasets, software, and supplementary research materials |
| Local archive / cloud archive / institutional repositories | Preservation and redundancy |

---

## 11. Landing Page Generation

EPINOVA uses a static landing-page generation workflow.

### 11.1 Source Files

Each publication folder contains:

```text
metadata.json
publication.pdf
```

### 11.2 Generator Script

Landing pages are generated using:

```text
tools/generate_landing_pages.py
```

The script reads all `metadata.json` files and generates:

```text
docs/index.html
docs/<publication-slug>/index.html
docs/<category>/index.html
docs/files/<publication-slug>/<publication.pdf>
docs/assets/global-ai-governance-logo.png
```

### 11.3 Cloudflare Pages

The generated `docs/` directory is deployed through Cloudflare Pages.

Recommended Cloudflare Pages settings:

```text
Framework preset: None
Build command: blank
Build output directory: docs
Root directory: blank
Branch: main
```

If Cloudflare is configured to run the generator automatically, the build command may be:

```text
python tools/generate_landing_pages.py
```

However, the recommended stable workflow is:

1. Run the generator locally.
2. Verify the generated pages.
3. Commit and push the generated `docs/` directory.
4. Let Cloudflare publish the static `docs/` output.

---

## 12. Standard Workflow

### Step 1. Prepare Publication Folder

Create a folder for the publication and add:

```text
publication.pdf
metadata.json
```

### Step 2. Update Metadata Links

Run:

```powershell
python tools\update_metadata_links.py
```

This updates:

- PDF filename
- PDF GitHub URL
- Repository folder URL
- ORCID
- DOI pending statement
- Crossref DOI suffix
- Citation pending DOI wording

### Step 3. Generate Landing Pages

Run:

```powershell
python tools\generate_landing_pages.py
```

### Step 4. Local Preview

Run:

```powershell
cd docs
python -m http.server 8000
```

Open:

```text
http://localhost:8000/
```

### Step 5. Commit and Push

```powershell
git status
git add .
git commit -m "Update EPINOVA publication records"
git push
```

### Step 6. Cloudflare Deployment

Cloudflare Pages publishes the updated `docs/` directory.

---

## 13. Platform Integration

EPINOVA research outputs follow a multi-layer publication infrastructure.

| Layer | Platform | Function |
|---|---|---|
| Institutional Portal | `epinova.org` | Public-facing institutional and research portal |
| DOI Landing Pages | `publications.epinova.org` | Official publication landing pages |
| Structure | GitHub | Repository, metadata, version control, and publication source records |
| DOI Registration | Crossref | DOI and metadata registration for EPINOVA publications |
| Data Archive | DataCite-based repositories / OSF / Figshare / Dataverse | Datasets, software, and supplementary research materials |
| Long-term Backup | Local archive / cloud archive / institutional repositories | Preservation and redundancy |

---

## 14. Quality Control Checklist

Before publication, each record should be checked for:

- Correct title
- Correct EPINOVA ID
- Correct publication type
- Correct publication date
- Complete creator information
- Correct ORCID
- Correct abstract and description
- Correct PDF file
- Correct `files` field
- Correct `repository_folder`
- Correct landing page URL
- Correct previous DOI, if applicable
- Correct DOI pending statement or assigned DOI
- Complete references
- Correct license
- Correct recommended citation
- Correct APA citation
- Working PDF preview
- Working download link
- Working Cloudflare deployment

---

## 15. Purpose

This publication system enables:

- Standardized citation
- Cross-publication traceability
- DOI-ready metadata management
- Scalable research output management
- Institutional-level knowledge production
- Long-term publication preservation
- Interoperability with Crossref, ORCID, GitHub, and public indexing systems

---

EPINOVA – Global AI Governance and Policy Research Center
