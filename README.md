# EPINOVA Research

**Global AI Governance and Policy Research Center, EPINOVA LLC**

AI governance · Systemic risk · Infrastructure · Policy intelligence

---

## Overview

This repository serves as the research evidence layer for EPINOVA publications.

It provides structured access to selected research outputs, including:

- books, policy briefs, reports, and working papers;
- conceptual frameworks, white papers, journal articles, book chapters, and index methodology papers;
- metadata records and publication source files;
- supporting materials for external dissemination and long-term reference.

Selected materials are provided for transparency, traceability, and public reference.

Due to the evolving and strategic nature of EPINOVA research, certain datasets, parameter configurations, internal evaluation procedures, and analytical workflows are maintained as internal assets.

---

## Research Focus

EPINOVA research focuses on:

- AI governance and regulatory frameworks;
- systemic risk and escalation dynamics;
- infrastructure-centered strategic analysis;
- policy intelligence and cross-domain integration;
- AI-enabled institutional, economic, and security transformation.

---

## Publication Infrastructure

EPINOVA uses a multi-layer publication infrastructure:

| Layer | Platform | Function |
|---|---|---|
| Institutional Portal | https://epinova.org | Public-facing institutional and research portal |
| Publication Landing Pages | https://publications.epinova.org | Official publication landing pages and DOI interface |
| Repository Layer | GitHub | Metadata, PDF records, version control, and publication source structure |
| DOI Registration | Crossref | DOI and metadata registration for EPINOVA publications |
| Internal Archive | Local archive / cloud archive | Preservation, redundancy, and internal research continuity |

Before Crossref DOI registration is completed, EPINOVA publication records may use internal publication identifiers and GitHub-based source folders. After Crossref registration, EPINOVA publication landing pages are intended to serve as the primary DOI resolution interface.

---

## Repository Structure

```text
EPINOVA-Research/
├── Articles/
├── Book/
├── Index Methodology Paper/
├── Journal Article/
├── White Paper/
├── Policy Brief/
├── Policy Report/
├── Research Report/
├── Working Paper/
├── assets/
├── doc/
├── docs/
└── tools/
```

Each publication source folder typically contains:

```text
publication.pdf
metadata.json
```

Book records may additionally contain:

```text
cover.png
crossref.xml
README.md
sample.pdf
```

The repository is the source and version-traceability layer for EPINOVA publications. The primary public access layer is the EPINOVA publication landing-page system, while DOI metadata is registered through Crossref when available.

The `Book/` directory is used for formally published books, monographs, reference works, edited books, and individual volumes in multi-volume publications issued by EPINOVA Press. Each independently published volume should have its own internal publication identifier, ISBN, DOI record, metadata file, and landing page.

For commercially distributed books, the public repository should normally contain metadata, cover files, sample material, Crossref deposit files, and record documentation rather than the complete sale edition.

The `Index Methodology Paper/` directory is used for index-construction and measurement-framework publications, including indicator architecture, normalization, weighting, classification, validation, and scoring methodology.

The `Journal Article/` directory is used for externally published or journal-style articles, including author-archived versions, publication records, magazine articles, and scholarly articles published outside the EPINOVA report series.

The `Conference Paper/` directory is used for full conference papers, proceedings papers, and independently citable conference contributions. Conference abstracts may be included only when they are treated as standalone publication records.

The `White Paper/` directory is used for broader institutional white papers, conceptual frameworks, policy architectures, and strategic framework documents.

The `docs/` directory contains the generated static publication site deployed through Cloudflare Pages.
## Publication Type Codes

| Publication Type | Code | Use |
|---|---:|---|
| Book | BK | Monographs, reference works, edited books, multi-volume works, and formally published standalone books issued by EPINOVA Press. |
| Index Methodology Paper | IMP | Index construction, measurement frameworks, indicator architecture, normalization, weighting, classification, validation, and scoring systems. |
| Journal Article | JA | Externally published or journal-style articles, including author-archived versions, publication records, magazine articles, and scholarly articles published outside the EPINOVA report series. |
| Conference Paper | CP | Full conference papers, proceedings papers, and independently citable conference contributions presented or published through academic and professional conferences. |
| White Paper | WHT | Institutional white papers presenting conceptual frameworks, policy architectures, strategic research, and official EPINOVA framework documents. |
| Policy Brief | PB | Concise policy analysis, strategic assessment, crisis interpretation, and actionable recommendations. |
| Policy Report | PR | Policy-facing reports with more detailed background, evidence, and institutional implications. |
| Research Report | RR | Full research reports, case studies, empirical analysis, and extended analytical outputs. |
| Working Paper | WP | Academic drafts, theoretical exploration, pre-publication research, and developing arguments. |
| Book Chapter | BCH | Individually registered chapters or entries within EPINOVA books when chapter-level DOI registration is used. |

Notes:

- `BK` is used for formally published books, monographs, reference works, and individual volumes in a multi-volume publication.
- `BCH` is reserved for book chapters or reference entries that receive independent chapter-level DOI registration.
- A book and its individual volumes should receive separate identifiers when each volume has distinct publication metadata, ISBN, and landing page.
- EPUB and PDF manifestations of the same edition should normally share the same DOI unless the format materially changes how the work is cited.
- Series relationships should be expressed through publication metadata rather than encoded into hierarchical DOI suffixes.
- `WP` is reserved for Working Paper.
- `WHT` is used for White Paper. The code is derived from “White” to avoid conflict with `WP`.
- `IMP` is used for Index Methodology Paper, especially documents focused on how an index is constructed, measured, weighted, validated, and applied.
- `JA` is used for Journal Article, especially externally published articles or author-archived article records that should not be mixed into EPINOVA policy brief/report numbering.
- `CP` is used for Conference Paper, including proceedings papers and independently citable conference contributions. The recommended identifier format is `EPINOVA-2026-CP-01`.
- For index projects, use `IMP` when the document is primarily methodological, and use `WHT` when the document is broader, more policy-facing, or intended as an institutional white paper.
## Latest Publications

The links below prioritize EPINOVA publication landing pages where available. GitHub links are retained as source-folder and source-file references for transparency, preservation, and version traceability.

### DOI and Access Notice

EPINOVA publication landing pages serve as the primary public access layer for current publication records. Crossref DOI records are used as the formal DOI registration layer when available.

During the Crossref migration period, existing Zenodo/DataCite DOI records may be displayed as temporary archival DOI links. These identifiers are retained for continuity, citation traceability, and archival access, but they may later be superseded by Crossref DOI records.

For newly prepared records that have not yet completed Crossref registration and do not have a temporary archival DOI, use the following temporary status statement:

```text
DOI: Temporary archival DOI shown when available; otherwise to be assigned or updated after Crossref registration.
```

### Books

- **EPINOVA-BK-2026-005** (2026-06-30)  
  **Global Artificial Intelligence Development and Competitiveness Assessment Framework: Frontier Indicators and Future Outlook**  
  Publication page: [https://publications.epinova.org/epinova-bk-2026-005/](https://publications.epinova.org/epinova-bk-2026-005/)  
  DOI: [10.67037/epinova.bk.2026.005](https://doi.org/10.67037/epinova.bk.2026.005)  
  Source folder: [`Book/EPINOVA-BK-2026-005/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Book/EPINOVA-BK-2026-005)  
  Source PDF: [`Volume IV Frontier Indicators and Future Outlook..pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Book/EPINOVA-BK-2026-005/Volume%20IV%20Frontier%20Indicators%20and%20Future%20Outlook..pdf)

- **EPINOVA-BK-2026-004** (2026-06-30)  
  **Global Artificial Intelligence Development and Competitiveness Assessment Framework: Governance, Risk, and Human Capital**  
  Publication page: [https://publications.epinova.org/epinova-bk-2026-004/](https://publications.epinova.org/epinova-bk-2026-004/)  
  DOI: [10.67037/epinova.bk.2026.004](https://doi.org/10.67037/epinova.bk.2026.004)  
  Source folder: [`Book/EPINOVA-BK-2026-004/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Book/EPINOVA-BK-2026-004)  
  Source PDF: [`Volume III Governance, Risk, and Human Capital.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Book/EPINOVA-BK-2026-004/Volume%20III%20Governance%2C%20Risk%2C%20and%20Human%20Capital.pdf)

- **EPINOVA-BK-2026-003** (2026-06-30)  
  **Global Artificial Intelligence Development and Competitiveness Assessment Framework: Algorithms, Applications, and Competitiveness**  
  Publication page: [https://publications.epinova.org/epinova-bk-2026-003/](https://publications.epinova.org/epinova-bk-2026-003/)  
  DOI: [10.67037/epinova.bk.2026.003](https://doi.org/10.67037/epinova.bk.2026.003)  
  Source folder: [`Book/EPINOVA-BK-2026-003/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Book/EPINOVA-BK-2026-003)  
  Source PDF: [`Volume II Algorithms, Applications, and Competitiveness.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Book/EPINOVA-BK-2026-003/Volume%20II%20Algorithms%2C%20Applications%2C%20and%20Competitiveness.pdf)

- **EPINOVA-BK-2026-002** (2026-06-30)  
  **Global Artificial Intelligence Development and Competitiveness Assessment Framework: AI Infrastructure and Foundational Capacity**  
  Publication page: [https://publications.epinova.org/epinova-bk-2026-002/](https://publications.epinova.org/epinova-bk-2026-002/)  
  DOI: [10.67037/epinova.bk.2026.002](https://doi.org/10.67037/epinova.bk.2026.002)  
  Source folder: [`Book/EPINOVA-BK-2026-002/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Book/EPINOVA-BK-2026-002)  
  Source PDF: [`Volume I AI Infrastructure and Foundational Capacity.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Book/EPINOVA-BK-2026-002/Volume%20I%20AI%20Infrastructure%20and%20Foundational%20Capacity.pdf)

- **EPINOVA-BK-2026-001** (2026-06-30)  
  **Global Artificial Intelligence Development and Competitiveness Assessment Framework: Complete Four-Volume Edition**  
  Publication page: [https://publications.epinova.org/epinova-bk-2026-001/](https://publications.epinova.org/epinova-bk-2026-001/)  
  DOI: [10.67037/epinova.bk.2026.001](https://doi.org/10.67037/epinova.bk.2026.001)  
  Source folder: [`Book/EPINOVA-BK-2026-001/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Book/EPINOVA-BK-2026-001)  
  Source PDF: [`cover.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Book/EPINOVA-BK-2026-001/cover.pdf)

---

### Index Methodology Papers

- **EPINOVA-IMP-2026-001** (2026-05-08)  
  **Political Credit Index (PCI): Measuring Political Credibility as Strategic Intangible Capital**  
  Publication page: [https://epinova.org/publications](https://epinova.org/publications)  
  DOI: [10.67037/epinova.imp.2026.001](https://doi.org/10.67037/epinova.imp.2026.001)  
  Source folder: [`Index Methodology Paper/2026/IMP-2026-01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Index%20Methodology%20Paper/2026/IMP-2026-01)  
  Source PDF: [`Political Credit Index (PCI) Measuring Political Credibility as Strategic Intangible Capital.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Index%20Methodology%20Paper/2026/IMP-2026-01/Political%20Credit%20Index%20%28PCI%29%20Measuring%20Political%20Credibility%20as%20Strategic%20Intangible%20Capital.pdf)

- **EPINOVA-IMP-2025-001** (2025-12-31)  
  **Survivor Governance Risk Index (SGRI): Conceptual and Methodological White Paper: Version 0.1 Foundational Release**  
  Publication page: [https://publications.epinova.org/epinova-imp-2025-001/](https://publications.epinova.org/epinova-imp-2025-001/)  
  Temporary archival DOI: [10.5281/zenodo.18050662](https://doi.org/10.5281/zenodo.18050662)  
  Source folder: [`Index Methodology Paper/2025/IWP–25–01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Index%20Methodology%20Paper/2025/IWP%E2%80%9325%E2%80%9301)  
  Source PDF: [`Survivor Governance Risk Index Conceptual and Methodological White Book.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Index%20Methodology%20Paper/2025/IWP%E2%80%9325%E2%80%9301/Survivor%20Governance%20Risk%20Index%20Conceptual%20and%20Methodological%20White%20Book.pdf)

---

### Journal Articles

- **EPINOVA-2026-JA-01** (2026-04)  
  **The Strait of Hormuz and the Partial De-Universalization of the Petrodollar: Chokepoint Power and Settlement Control in the Gulf Energy Order**  
  Publication page: [https://publications.epinova.org/epinova-2026-ja-01/](https://publications.epinova.org/epinova-2026-ja-01/)  
  DOI: To be assigned or updated after Crossref registration.  
  Source folder: [`Journal Article/2026/EPINOVA-2026-JA-01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Journal%20Article/2026/EPINOVA-2026-JA-01)  
  Source PDF: [`The Strait of Hormuz and the Partial De-Universalization of the Petrodollar Chokepoint Power and Settlement Control in the Gulf Energy Order.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Journal%20Article/2026/EPINOVA-2026-JA-01/The%20Strait%20of%20Hormuz%20and%20the%20Partial%20De-Universalization%20of%20the%20Petrodollar%20Chokepoint%20Power%20and%20Settlement%20Control%20in%20the%20Gulf%20Energy%20Order.pdf)

---

### White Papers

- **EPINOVA-IWB-2026-001** (2026-01-31)  
  **AI-Strategic Node Framework (AI-SNF): Conceptual and Methodological White Paper: Version 0.1 Foundational Release**  
  Publication page: [https://epinova.org/iwb2601](https://epinova.org/iwb2601)  
  Temporary archival DOI: [10.5281/zenodo.18452803](https://doi.org/10.5281/zenodo.18452803)  
  Source folder: [`White Paper/2026/IWB-2026-01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/White%20Paper/2026/IWB-2026-01)  
  Source PDF: [`AI-Strategic Node Framework (AI-SNF) Conceptual and Methodological White Book.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/White%20Paper/2026/IWB-2026-01/AI-Strategic%20Node%20Framework%20%28AI-SNF%29%20Conceptual%20and%20Methodological%20White%20Book.pdf)

---

### Policy Briefs

- **EPINOVA-PB-2026-071** (2026-09-07)  
  **The Machine Audience of War: AI-Generated Video, Narrative Occupancy, and Machine-Mediated Information Competition in the U.S.–Israel–Iran Conflict**  
  Publication page: [https://epinova.org/policy-brief-1](https://epinova.org/policy-brief-1)  
  DOI: [10.67037/epinova.pb.2026.071](https://doi.org/10.67037/epinova.pb.2026.071)  
  Source folder: [`Policy Brief/2026/EPINOVA–2026–PB-71/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-71)  
  Source PDF: [`The Machine Audience of War AI-Generated Video, Narrative Occupancy, and Machine-Mediated Information Competition in the U.S.–Israel–Iran Conflict.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-71/The%20Machine%20Audience%20of%20War%20AI-Generated%20Video%2C%20Narrative%20Occupancy%2C%20and%20Machine-Mediated%20Information%20Competition%20in%20the%20U.S.%E2%80%93Israel%E2%80%93Iran%20Conflict.pdf)

- **EPINOVA-PB-2026-070** (2026-08-28)  
  **Japan's Rising Strategic Value and the Potential Restructuring of the Asia-Pacific Order**  
  Publication page: [https://epinova.org/policy-brief-1](https://epinova.org/policy-brief-1)  
  DOI: [10.67037/epinova.pb.2026.070](https://doi.org/10.67037/epinova.pb.2026.070)  
  Source folder: [`Policy Brief/2026/EPINOVA–2026–PB-70/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-70)  
  Source PDF: [`Japan's Rising Strategic Value and the Potential Restructuring of the Asia-Pacific Order.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-70/Japan%27s%20Rising%20Strategic%20Value%20and%20the%20Potential%20Restructuring%20of%20the%20Asia-Pacific%20Order.pdf)

- **EPINOVA-PB-2026-069** (2026-08-17)  
  **From AI-Enabled Weapons to AI-Orchestrated Warfare: The Emerging Global Military AI Stack in 2026**  
  Publication page: [https://epinova.org/policy-brief-1](https://epinova.org/policy-brief-1)  
  DOI: [10.67037/epinova.pb.2026.069](https://doi.org/10.67037/epinova.pb.2026.069)  
  Source folder: [`Policy Brief/2026/EPINOVA–2026–PB-69/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-69)  
  Source PDF: [`From AI-Enabled Weapons to AI-Orchestrated Warfare The Emerging Global Military AI Stack in 2026.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-69/From%20AI-Enabled%20Weapons%20to%20AI-Orchestrated%20Warfare%20The%20Emerging%20Global%20Military%20AI%20Stack%20in%202026.pdf)

- **EPINOVA-PB-2026-068** (2026-08-12)  
  **Iran After Succession: Power, Access, and Institutional Rebalancing under Mojtaba Khamenei**  
  Publication page: [https://epinova.org/policy-brief-1](https://epinova.org/policy-brief-1)  
  DOI: [10.67037/epinova.pb.2026.068](https://doi.org/10.67037/epinova.pb.2026.068)  
  Source folder: [`Policy Brief/2026/EPINOVA–2026–PB-68/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-68)  
  Source PDF: [`Iran After Succession Power, Access, and Institutional Rebalancing under Mojtaba Khamenei.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-68/Iran%20After%20Succession%20Power%2C%20Access%2C%20and%20Institutional%20Rebalancing%20under%20Mojtaba%20Khamenei.pdf)

- **EPINOVA-PB-2026-067** (2026-08-10)  
  **Rerouting the Gulf: Bypass Infrastructure and the Changing Strategic Value of the Strait of Hormuz**  
  Publication page: [https://epinova.org/policy-brief-1](https://epinova.org/policy-brief-1)  
  DOI: [10.67037/epinova.pb.2026.067](https://doi.org/10.67037/epinova.pb.2026.067)  
  Source folder: [`Policy Brief/2026/EPINOVA–2026–PB-67/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-67)  
  Source PDF: [`Rerouting the Gulf Bypass Infrastructure and the Changing Strategic Value of the Strait of Hormuz.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Brief/2026/EPINOVA%E2%80%932026%E2%80%93PB-67/Rerouting%20the%20Gulf%20Bypass%20Infrastructure%20and%20the%20Changing%20Strategic%20Value%20of%20the%20Strait%20of%20Hormuz.pdf)

---

### Policy Reports

- **EPINOVA-PR-2025-001** (2025-12-31)  
  **Nonlinear Uncertainty in Drone Warfare: Why Indeterminacy Outperforms Precision in Contested ISR Environments**  
  Publication page: [https://epinova.org/publications](https://epinova.org/publications)  
  Temporary archival DOI: [10.5281/zenodo.18111066](https://doi.org/10.5281/zenodo.18111066)  
  Source folder: [`Policy Report/2025/EPINOVA–2025–PR–01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Policy%20Report/2025/EPINOVA%E2%80%932025%E2%80%93PR%E2%80%9301)  
  Source PDF: [`Nonlinear Uncertainty in Drone Warfare Why Indeterminacy Outperforms Precision in Contested ISR Environments.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Policy%20Report/2025/EPINOVA%E2%80%932025%E2%80%93PR%E2%80%9301/Nonlinear%20Uncertainty%20in%20Drone%20Warfare%20Why%20Indeterminacy%20Outperforms%20Precision%20in%20Contested%20ISR%20Environments.pdf)

---

### Research Reports

- **EPINOVA-RR-2026-002** (2026-09-15)  
  **The U.S.–Israel–Iran Conflict on Day 200: Strategic Objectives, Systemic Costs, and the Rewiring of Networked War**  
  Publication page: [https://epinova.org/research-reports](https://epinova.org/research-reports)  
  DOI: [10.67037/epinova.rr.2026.002](https://doi.org/10.67037/epinova.rr.2026.002)  
  Source folder: [`Research Report/2026/EPINOVA–2026–RR-02/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Research%20Report/2026/EPINOVA%E2%80%932026%E2%80%93RR-02)  
  Source PDF: [`The U.S.–Israel–Iran Conflict on Day 200 Strategic Objectives, Systemic Costs, and the Rewiring of Networked War.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Research%20Report/2026/EPINOVA%E2%80%932026%E2%80%93RR-02/The%20U.S.%E2%80%93Israel%E2%80%93Iran%20Conflict%20on%20Day%20200%20Strategic%20Objectives%2C%20Systemic%20Costs%2C%20and%20the%20Rewiring%20of%20Networked%20War.pdf)

- **EPINOVA-RR-2026-001** (2026-09-01)  
  **India’s AI Power in a Distributed and Uneven Technological Order: Boundary Control, Strategic Autonomy, and Cognitive Security**  
  Publication page: [https://epinova.org/research-reports](https://epinova.org/research-reports)  
  DOI: [10.67037/epinova.rr.2026.001](https://doi.org/10.67037/epinova.rr.2026.001)  
  Source folder: [`Research Report/2026/EPINOVA–2026–RR-01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Research%20Report/2026/EPINOVA%E2%80%932026%E2%80%93RR-01)  
  Source PDF: [`India’s AI Power in a Distributed and Uneven Technological Order Boundary Control, Strategic Autonomy, and Cognitive Security.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Research%20Report/2026/EPINOVA%E2%80%932026%E2%80%93RR-01/India%E2%80%99s%20AI%20Power%20in%20a%20Distributed%20and%20Uneven%20Technological%20Order%20Boundary%20Control%2C%20Strategic%20Autonomy%2C%20and%20Cognitive%20Security.pdf)

- **EPINOVA-RR-2025-001** (2025-12-31)  
  **From Detection to Depletion: Cost-Exchange Limits in the Russia–Ukraine Drone War**  
  Publication page: [https://epinova.org/publications](https://epinova.org/publications)  
  Temporary archival DOI: [10.5281/zenodo.18036790](https://doi.org/10.5281/zenodo.18036790)  
  Source folder: [`Research Report/2025/EPINOVA–2025–01–RR/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Research%20Report/2025/EPINOVA%E2%80%932025%E2%80%9301%E2%80%93RR)  
  Source PDF: [`From Detection to Depletion Cost-Exchange Limits in the Russia–Ukraine Drone War.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Research%20Report/2025/EPINOVA%E2%80%932025%E2%80%9301%E2%80%93RR/From%20Detection%20to%20Depletion%20Cost-Exchange%20Limits%20in%20the%20Russia%E2%80%93Ukraine%20Drone%20War.pdf)

---

### Working Papers

#### WP-F — Conflict, Escalation, and Networked Warfare

- **EPINOVA-WP-F-2026-012** (2026-09-03)  
  **The Decoupling of Geographic and Strategic Distance: Homeland Vulnerability, Effect Projection, and System Defense in Networked Warfare**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.f.2026.012](https://doi.org/10.67037/epinova.wp.f.2026.012)  
  Source folder: [`Working Paper/F/2026/PINOVA–WP–F–2026–12/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9312)  
  Source PDF: [`The Decoupling of Geographic and Strategic Distance Homeland Vulnerability, Effect Projection, and System Defense in Networked Warfare.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9312/The%20Decoupling%20of%20Geographic%20and%20Strategic%20Distance%20Homeland%20Vulnerability%2C%20Effect%20Projection%2C%20and%20System%20Defense%20in%20Networked%20Warfare.pdf)

- **EPINOVA-WP-F-2026-011** (2026-06-18)  
  **From Wartime Leverage to Post-MOU State Capacity: Iran’s Reconstruction, Institutional Recovery, and Strategic Network Rebalancing**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.f.2026.011](https://doi.org/10.67037/epinova.wp.f.2026.011)  
  Source folder: [`Working Paper/F/2026/PINOVA–WP–F–2026–11/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9311)  
  Source PDF: [`From Wartime Leverage to Post-MOU State Capacity Iran’s Reconstruction, Institutional Recovery, and Strategic Network Rebalancing.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9311/From%20Wartime%20Leverage%20to%20Post-MOU%20State%20Capacity%20Iran%E2%80%99s%20Reconstruction%2C%20Institutional%20Recovery%2C%20and%20Strategic%20Network%20Rebalancing.pdf)

- **EPINOVA-WP-F-2026-010** (2026-06-16)  
  **The War That Measured America: Why Washington Entered the U.S.–Iran Conflict, What It Revealed, and How It Accelerated a Eurasian Counter-System**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.f.2026.010](https://doi.org/10.67037/epinova.wp.f.2026.010)  
  Source folder: [`Working Paper/F/2026/PINOVA–WP–F–2026–10/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9310)  
  Source PDF: [`The War That Measured America Why Washington Entered the U.S.–Iran Conflict, What It Revealed, and How It Accelerated a Eurasian Counter-System.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/F/2026/PINOVA%E2%80%93WP%E2%80%93F%E2%80%932026%E2%80%9310/The%20War%20That%20Measured%20America%20Why%20Washington%20Entered%20the%20U.S.%E2%80%93Iran%20Conflict%2C%20What%20It%20Revealed%2C%20and%20How%20It%20Accelerated%20a%20Eurasian%20Counter-System.pdf)

#### WP-D — Data Centers, Infrastructure, and Local Governance

- **EPINOVA-WP-D-2026-003** (2026-08-21)  
  **Toward Measuring AI Infrastructure Investment and Economic Resilience Across Ten Economies: Financing Architectures, Capital Formation, and Deployment Timing**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.d.2026.003](https://doi.org/10.67037/epinova.wp.d.2026.003)  
  Source folder: [`Working Paper/D/2026/EPINOVA–WP–D–2026–03/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9303)  
  Source PDF: [`Toward Measuring AI Infrastructure Investment and Economic Resilience Across Ten Economies Financing Architectures, Capital Formation, and Deployment Timing.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9303/Toward%20Measuring%20AI%20Infrastructure%20Investment%20and%20Economic%20Resilience%20Across%20Ten%20Economies%20Financing%20Architectures%2C%20Capital%20Formation%2C%20and%20Deployment%20Timing.pdf)

- **EPINOVA-WP-D-2026-002** (2026-02-09)  
  **Why the South?: Institutional Friction and the Spatial Reorganization of Data Center Infrastructure in the United States**  
  Publication page: [https://doi.org/10.5281/zenodo.18572133](https://doi.org/10.5281/zenodo.18572133)  
  Temporary archival DOI: [10.5281/zenodo.18572133](https://doi.org/10.5281/zenodo.18572133)  
  Source folder: [`Working Paper/D/2026/EPINOVA–WP–D–2026–02/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9302)  
  Source PDF: [`Why the South.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9302/Why%20the%20South.pdf)

- **EPINOVA-WP-D-2026-001** (2026-02-02)  
  **When AI Infrastructure Is Optional but Governance Lock-In Is Not: An AI-SNI Local Governance Diagnostic of the Temple (GA) Data Center Proposal**  
  Publication page: [https://doi.org/10.5281/zenodo.18463740](https://doi.org/10.5281/zenodo.18463740)  
  Temporary archival DOI: [10.5281/zenodo.18463740](https://doi.org/10.5281/zenodo.18463740)  
  Source folder: [`Working Paper/D/2026/EPINOVA–WP–D–2026–01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9301)  
  Source PDF: [`When AI Infrastructure Is Optional but Governance Lock-In Is Not.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/D/2026/EPINOVA%E2%80%93WP%E2%80%93D%E2%80%932026%E2%80%9301/When%20AI%20Infrastructure%20Is%20Optional%20but%20Governance%20Lock-In%20Is%20Not.pdf)

#### WP-A — AI Strategic Nodes and Structural Governance

- **EPINOVA-WP-A-2026-004** (2026-06-12)  
  **Low-Observable Deployable Modular Surface Platform (LODMSP): From Fixed Decks to Deployable Mission Interfaces in Autonomous Maritime Systems**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.a.2026.004](https://doi.org/10.67037/epinova.wp.a.2026.004)  
  Source folder: [`Working Paper/A/2026/EPINOVA–WP–A–2026–04/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9304)  
  Source PDF: [`Low-Observable Deployable Modular Surface Platform (LODMSP) From Fixed Decks to Deployable Mission Interfaces in Autonomous Maritime Systems.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9304/Low-Observable%20Deployable%20Modular%20Surface%20Platform%20%28LODMSP%29%20From%20Fixed%20Decks%20to%20Deployable%20Mission%20Interfaces%20in%20Autonomous%20Maritime%20Systems.pdf)

- **EPINOVA-WP-A-2026-003** (2026-05-11)  
  **From Control Substitution to Structural Dominance: Morphological Convergence and Infrastructure Power in Autonomous Systems**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.a.2026.003](https://doi.org/10.67037/epinova.wp.a.2026.003)  
  Source folder: [`Working Paper/A/2026/EPINOVA–WP–A–2026–03/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9303)  
  Source PDF: [`From Control Substitution to Structural Dominance Beyond Morphology in the Age of Autonomous Systems.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9303/From%20Control%20Substitution%20to%20Structural%20Dominance%20Beyond%20Morphology%20in%20the%20Age%20of%20Autonomous%20Systems.pdf)

- **EPINOVA-WP-A-2026-002** (2026-04-24)  
  **Beyond Theater Effects: Perception-Driven Escalation and Loss-of-Control Thresholds in AI-Mediated Conflict**  
  Publication page: [https://doi.org/10.5281/zenodo.19734514](https://doi.org/10.5281/zenodo.19734514)  
  Temporary archival DOI: [10.5281/zenodo.19734514](https://doi.org/10.5281/zenodo.19734514)  
  Source folder: [`Working Paper/A/2026/EPINOVA–WP–A–2026–02/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9302)  
  Source PDF: [`Beyond Theater Effects Perception-Driven Escalation and Loss-of-Control Thresholds in AI-Mediated Conflict.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/A/2026/EPINOVA%E2%80%93WP%E2%80%93A%E2%80%932026%E2%80%9302/Beyond%20Theater%20Effects%20Perception-Driven%20Escalation%20and%20Loss-of-Control%20Thresholds%20in%20AI-Mediated%20Conflict.pdf)

#### WP-T — Theory and Systems

- **EPINOVA-WP-T-2026-002** (2026-09-01)  
  **Two Structures of AI Power: National Capacity, Relational Boundary Control, and Systemic Influence in the Emerging AI Order**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.t.2026.002](https://doi.org/10.67037/epinova.wp.t.2026.002)  
  Source folder: [`Working Paper/T/2026/EPINOVA–WP–T–2026–02/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/T/2026/EPINOVA%E2%80%93WP%E2%80%93T%E2%80%932026%E2%80%9302)  
  Source PDF: [`Two Structures of AI Power National Capacity, Relational Boundary Control, and Systemic Influence in the Emerging AI Order.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/T/2026/EPINOVA%E2%80%93WP%E2%80%93T%E2%80%932026%E2%80%9302/Two%20Structures%20of%20AI%20Power%20National%20Capacity%2C%20Relational%20Boundary%20Control%2C%20and%20Systemic%20Influence%20in%20the%20Emerging%20AI%20Order.pdf)

- **EPINOVA-WP-T-2026-001** (2026-08-31)  
  **Beyond Centrality: Conditional Connectivity and Boundary Control in Interdependent Networks**  
  Publication page: [https://epinova.org/working-papers](https://epinova.org/working-papers)  
  DOI: [10.67037/epinova.wp.t.2026.01](https://doi.org/10.67037/epinova.wp.t.2026.01)  
  Source folder: [`Working Paper/T/2026/EPINOVA–WP–T–2026–01/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/T/2026/EPINOVA%E2%80%93WP%E2%80%93T%E2%80%932026%E2%80%9301)  
  Source PDF: [`Beyond Centrality Conditional Connectivity, Boundary Control, and Systemic Power in Interdependent Networks.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/T/2026/EPINOVA%E2%80%93WP%E2%80%93T%E2%80%932026%E2%80%9301/Beyond%20Centrality%20Conditional%20Connectivity%2C%20Boundary%20Control%2C%20and%20Systemic%20Power%20in%20Interdependent%20Networks.pdf)

#### WP-Other — Other Working Papers

- **EPINOVA-WP-2025-001** (2025-10-13)  
  **Gray-Zone Maritime Rights-Protection Strategy: Asymmetric Costs and Sustainable Presence, A Case Study of the China–Philippines Dispute over Scarborough Shoal**  
  Publication page: [https://doi.org/10.5281/zenodo.18095271](https://doi.org/10.5281/zenodo.18095271)  
  Temporary archival DOI: [10.5281/zenodo.18095271](https://doi.org/10.5281/zenodo.18095271)  
  Source folder: [`Working Paper/F/2025/2025-10-13/`](https://github.com/EPINOVALLC/EPINOVA-Research/tree/main/Working%20Paper/F/2025/2025-10-13)  
  Source PDF: [`Gray-Zone Maritime Rights-Protection Strategy.pdf`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/Working%20Paper/F/2025/2025-10-13/Gray-Zone%20Maritime%20Rights-Protection%20Strategy.pdf)
## Publication Metadata

EPINOVA publication records use structured `metadata.json` files. These records support:

- publication landing page generation;
- citation consistency;
- DOI registration preparation, including book- and chapter-level records;
- repository traceability;
- Crossref metadata readiness.

Publication pages are generated using:

```powershell
python tools\generate_landing_pages.py
```

Metadata links can be updated using:

```powershell
python tools\update_metadata_links.py
```

---

## Documentation

- Publication manual: [`doc/publication-manual.md`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/doc/publication-manual.md)
- Landing page generator: [`tools/generate_landing_pages.py`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/tools/generate_landing_pages.py)
- Metadata updater: [`tools/update_metadata_links.py`](https://github.com/EPINOVALLC/EPINOVA-Research/blob/main/tools/update_metadata_links.py)

---

## Data Source and Identifiers

- ORCID: https://orcid.org/0009-0008-0660-8232
- GitHub Repository: https://github.com/EPINOVALLC/EPINOVA-Research

---

## Platforms

- Website: https://epinova.org
- Publications: https://publications.epinova.org
- Repository: https://github.com/EPINOVALLC/EPINOVA-Research
- LinkedIn: https://www.linkedin.com/company/107228428

---

## Contact

Email: contactus@epinova.org  
Alternative contact: epinovallc@gmail.com

---

## Note on Data and Reproducibility

This repository provides selected materials for transparency, traceability, and public reference.

Due to the evolving and strategic nature of EPINOVA research, certain datasets, parameter configurations, internal evaluation procedures, and analytical processes are maintained as internal assets.

Where appropriate, public-facing publications are accompanied by metadata records, publication landing pages, internal identifiers, and selected supporting materials.

---

## License and Use

Unless otherwise specified in individual publication records, EPINOVA research outputs are released for scholarly reference, citation, and non-commercial academic use with proper attribution.

Specific license information is provided in each publication’s `metadata.json` record and corresponding landing page.

---

**EPINOVA – Global AI Governance and Policy Research Center**
