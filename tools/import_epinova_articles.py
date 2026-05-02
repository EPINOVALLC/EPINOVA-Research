import re
import json
import time
import mimetypes
import requests
import html2text
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
OUTPUT_DIR = ROOT / "Articles"

PUBLISHER = "Global AI Governance and Policy Research Center, EPINOVA LLC"
MIN_EXPECTED_ARTICLES = 40

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 EPINOVA Article Archiver"
}

CREATOR = {
    "name": "Shaoyuan Wu",
    "affiliation": PUBLISHER,
    "orcid": "https://orcid.org/0009-0008-0660-8232"
}

ARTICLE_CATALOG = [
    ("2026-04-21", "MCCM v2.3+: Escalation and the Loss-of-Control Threshold"),
    ("2026-04-12", "2026 MCCM 2.0+(23 Variables Ver.): April 12"),
    ("2026-04-11", "The Quiet Surge: How AI Procurement Is Reshaping the Logic of War"),
    ("2026-04-11", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 11"),
    ("2026-04-10", "SHI and Caspian Port Dynamics in Iran: April 9–10, 2026"),
    ("2026-04-10", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 10"),
    ("2026-04-09", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 9"),
    ("2026-04-08", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 8"),
    ("2026-04-07", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 7"),
    ("2026-04-06", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 6"),
    ("2026-04-05", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 5"),
    ("2026-04-04", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 4"),
    ("2026-04-03", "MCCM Daily War Cost Dynamics (K-Line): Feb 28–Apr 3, 2026"),
    ("2026-04-03", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 3"),
    ("2026-04-02", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 2"),
    ("2026-04-01", "MCCM Daily Direct War Cost by Actor: Feb 28 – Apr 1, 2026"),
    ("2026-04-01", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): April 1"),
    ("2026-03-31", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 31"),
    ("2026-03-31", "The Strategic Misalignment of U.S. Power"),
    ("2026-03-30", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 30"),
    ("2026-03-29", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 29"),
    ("2026-03-28", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 28"),
    ("2026-03-27", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 27"),
    ("2026-03-26", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 26"),
    ("2026-03-25", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 25"),
    ("2026-03-25", "Diverging Thresholds: The Emerging Strategic Split Between the United States and Israel in the Iran Conflict"),
    ("2026-03-24", "From Overmatch Deterrence to Cost Imposition: Structural Shifts in the U.S.–Iran Conflict"),
    ("2026-03-24", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 24"),
    ("2026-03-23", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 23"),
    ("2026-03-22", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 22"),
    ("2026-03-21", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 21"),
    ("2026-03-20", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 20"),
    ("2026-03-19", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 19"),
    ("2026-03-19", "War as Training Data: Ukraine and the Future of Datafied Conflict"),
    ("2026-03-18", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 18"),
    ("2026-03-17", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 17"),
    ("2026-03-16", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 16"),
    ("2026-03-15", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 15"),
    ("2026-03-14", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 14"),
    ("2026-03-13", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 13"),
    ("2026-03-12", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 12"),
    ("2026-03-11", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 11"),
    ("2026-03-10", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 10"),
    ("2026-03-09", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 9"),
    ("2026-03-08", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 8"),
    ("2026-03-07", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 7"),
    ("2026-03-06", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 6"),
    ("2026-03-05", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 5"),
    ("2026-03-04", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 4"),
    ("2026-03-03", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 3"),
    ("2026-03-02", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 2"),
    ("2026-03-01", "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 1"),
    ("2026-02-28", "2026 Middle East Conflict Cost Monitor (MCCM)"),
    ("2026-02-27", "Beyond Rankings: What Really Defines AI National Power?"),
    ("2026-02-09", "Why the South?"),
    ("2026-02-02", "When AI Infrastructure Is Optional but Governance Lock-In Is Not"),
    ("2026-01-15", "Greenland as a Structural AI Strategic Node: Perception Integrity, Temporal Dominance, and the Arctic Reconfiguration of Algorithmic Power"),
    ("2026-01-15", "When Decapitation No Longer Matters: AI-Delegated Execution and the Potential Failure of Preemptive Strike Logic"),
    ("2025-12-29", "Permanent Presence under Uncertainty: A Partially Observable Game-Theoretic Framework for Unmanned Systems, Cost–Frequency Dynamics, and Strategic Stability"),
    ("2025-12-26", "Artificial Intelligence as National Power: Implications of the 2025 U.S. National Security Strategy for AI Development"),
    ("2025-12-23", "A Fiber-Aware MVA Framework for Counter-UAS Assessment"),
    ("2025-12-20", "Survivor Governance: Authority Concentration under AI-Driven State Contraction"),
    ("2025-12-16", "From Space Infrastructure to AI State Capacity: South Korea’s National AI Trajectory Analysis Through KASA’s 2026 Strategy"),
    ("2025-12-12", "Strategic Discontinuity in AI-Enabled Warfare: Machine-Led vs Human-Led OODA"),
    ("2025-12-04", "Unmanned Algorithmic Warfare and Human Role Reconfiguration: An International Law Perspective"),
    ("2025-11-20", "Rethinking the Human–AI Division of Labor: From Irreplaceable Work to Meta-Functional Governance and Coevolution"),
    ("2025-11-15", "Single-/Few-Human–AI Firms and Single-/Few-Human–AI–Robot Firms: New Archetypes under the MMC Framework"),
    ("2025-10-20", "Geopolitical Consequences of Cloud Outages: The Systemic Risks of AWS Architecture, National Security, and Digital Sovereignty"),
    ("2025-10-13", "Gray-Zone Maritime Rights-Protection Strategy: Asymmetric Costs and Sustainable Presence, A Case Study of the China–Philippines Dispute over Scarborough Shoal"),
    ("2025-05-10", "An Analysis of the 2025 India-Pakistan Conflict: From Regional Flashpoint to Global Faultline"),
    ("2025-05-05", "Epistemic Humility in AGI: Toward Ethical & Adaptive Intelligence"),
    ("2025-05-03", "Pinocchio or Frankenstein: AGI Frameworks Review and Forward"),
    ("2025-04-08", "AI: From Information Cocoon to Cognitive Cocoon?"),
    ("2025-02-13", "How AI and Corporate Principles Are Reshaping Government?"),
]

MANUAL_URL_OVERRIDES = {
    # Short / encoded GoDaddy URLs that should bypass slug reconstruction.
    "MCCM Daily Direct War Cost by Actor: Feb 28 – Apr 1, 2026":
        "https://epinova.org/articles/f/mccm-daily-direct-war-cost-by-actor-feb-28-%E2%80%93-apr-1-2026",
    "MCCM Daily Direct War Cost by Actor: Feb 28 - Apr 1, 2026":
        "https://epinova.org/articles/f/mccm-daily-direct-war-cost-by-actor-feb-28-%E2%80%93-apr-1-2026",

    "Diverging Thresholds: The Emerging Strategic Split Between the United States and Israel in the Iran Conflict":
        "https://epinova.org/articles/f/diverging-thresholds",

    "From Overmatch Deterrence to Cost Imposition: Structural Shifts in the U.S.–Iran Conflict":
        "https://epinova.org/articles/f/from-overmatch-deterrence-to-cost-imposition",
    "From Overmatch Deterrence to Cost Imposition: Structural Shifts in the U.S.-Iran Conflict":
        "https://epinova.org/articles/f/from-overmatch-deterrence-to-cost-imposition",

    # The live page URL uses March 15-1 although the catalog title is March 16.
    "2026 U.S. & Allies–Iran Conflict Cost Monitor (MCCM): March 16":
        "https://epinova.org/articles/f/2026-us-allies%E2%80%93iran-conflict-cost-monitor-mccm-march-15-1",
    "2026 U.S. & Allies-Iran Conflict Cost Monitor (MCCM): March 16":
        "https://epinova.org/articles/f/2026-us-allies%E2%80%93iran-conflict-cost-monitor-mccm-march-15-1",

    "Single-/Few-Human–AI Firms and Single-/Few-Human–AI–Robot Firms: New Archetypes under the MMC Framework":
        "https://epinova.org/articles/f/single-few-human%E2%80%93ai-firms-and-single-few-human%E2%80%93ai%E2%80%93robot-firms",
    "Single-/Few-Human-AI Firms and Single-/Few-Human-AI-Robot Firms: New Archetypes under the MMC Framework":
        "https://epinova.org/articles/f/single-few-human%E2%80%93ai-firms-and-single-few-human%E2%80%93ai%E2%80%93robot-firms",

    # This is not the Single/Few-Human page; keep it as its own short-slug override.
    "Greenland as a Structural AI Strategic Node: Perception Integrity, Temporal Dominance, and the Arctic Reconfiguration of Algorithmic Power":
        "https://epinova.org/articles/f/greenland-as-a-structural-ai-strategic-node",
}


def normalize_text_for_match(text: str) -> str:
    text = (text or "")
    text = text.replace("&amp;", "&")
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def get_manual_url_override(title: str) -> str | None:
    clean_title = " ".join((title or "").split())
    if clean_title in MANUAL_URL_OVERRIDES:
        return MANUAL_URL_OVERRIDES[clean_title]

    clean_key = normalize_text_for_match(clean_title)
    for key, url in MANUAL_URL_OVERRIDES.items():
        if normalize_text_for_match(key) == clean_key:
            return url
    return None


def manual_url_warning(title: str, url: str) -> str:
    title_norm = normalize_text_for_match(title)
    url_norm = normalize_text_for_match(url)
    if "greenland" in title_norm and "single-few-human" in url_norm:
        return "WARNING: title is Greenland, but URL appears to be Single-/Few-Human-AI. Check catalog mapping."
    if "single" in title_norm and "greenland" in url_norm:
        return "WARNING: title is Single-/Few-Human-AI, but URL appears to be Greenland. Check catalog mapping."
    return ""


def normalize_slug(text: str) -> str:
    text = (text or "").strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("&", "and")
    text = text.replace("+", "plus")
    text = text.replace("?", "")
    text = text.replace(":", "")
    text = text.replace("(", "").replace(")", "")
    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("/", "-").replace("\\", "-")
    text = text.replace(" ", "-")
    text = re.sub(r"[^a-z0-9\-]+", "", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "untitled"


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    url = url.replace("\\/", "/")
    url = url.replace("&amp;", "&")
    url = url.split("#")[0]
    url = url.split("?")[0]
    return url.rstrip(".").rstrip("/")


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def compact_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(text).lower())


def html_escape(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_page(url: str) -> tuple[str, str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=REQUEST_HEADERS["User-Agent"])
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(8000)
        html = page.content()
        visible_text = page.evaluate("() => document.body.innerText")
        final_url = normalize_url(page.url)
        browser.close()
        return html, visible_text, final_url


def mccm_daily_slug(title: str) -> str | None:
    m = re.search(r":\s*(March|April)\s+(\d{1,2})$", title)
    if not m:
        return None

    month = m.group(1).lower()
    day = m.group(2)

    if "U.S. & Allies–Iran Conflict Cost Monitor" in title:
        return f"2026-us-allies%E2%80%93iran-conflict-cost-monitor-mccm-{month}-{day}"

    return None


def slug_variants(slug: str) -> list[str]:
    """
    Generate likely GoDaddy slug variants.
    Handles en dash encoded as %E2%80%93, em dash, shortened long titles,
    and common AI/geopolitical compounds.
    """
    base = slug.strip("/")
    variants = [base]

    # Date/number ranges: 9-10 -> 9%E2%80%9310; feb-28-apr -> feb-28%E2%80%93apr
    variants.append(re.sub(r"(?<=\d)-(?=\d)", "%E2%80%93", base))
    variants.append(re.sub(r"(?<=\d)-(?=[a-z])", "%E2%80%93", base))

    replacements = {
        "human-ai": "human%E2%80%93ai",
        "ai-human": "ai%E2%80%93human",
        "ai-robot": "ai%E2%80%93robot",
        "human-ai-robot": "human%E2%80%93ai%E2%80%93robot",
        "allies-iran": "allies%E2%80%93iran",
        "us-allies-iran": "us-allies%E2%80%93iran",
        "china-philippines": "china%E2%80%93philippines",
        "cost-frequency": "cost%E2%80%93frequency",
        "machine-led": "machine%E2%80%93led",
        "human-led": "human%E2%80%93led",
        "9-10": "9%E2%80%9310",
        "28-apr": "28%E2%80%93apr",
        "apr-1": "apr%E2%80%931",
    }

    for old, new in replacements.items():
        if old in base:
            variants.append(base.replace(old, new))

    # Long-title truncation variants.
    cut_markers = [
        "-perception-integrity",
        "-temporal-dominance",
        "-and-the-arctic",
        "-ai-delegated-execution",
        "-the-potential-failure",
        "-a-partially-observable",
        "-game-theoretic-framework",
        "-cost-frequency",
        "-and-strategic-stability",
        "-authority-concentration",
        "-under-ai-driven",
        "-machine-led-vs-human-led",
        "-an-international-law-perspective",
        "-from-irreplaceable-work",
        "-meta-functional-governance",
        "-new-archetypes",
        "-under-the-mmc-framework",
        "-asymmetric-costs",
        "-a-case-study",
        "-from-regional-flashpoint",
        "-to-global-faultline",
    ]

    for marker in cut_markers:
        if marker in base:
            variants.append(base.split(marker)[0])

    out = []
    seen = set()
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def catalog_to_seed_urls() -> list[dict]:
    manual = {
        # MCCM / AIPAMS series
        "MCCM v2.3+: Escalation and the Loss-of-Control Threshold":
            "mccm-v23-escalation-and-the-loss-of-control-threshold",
        "2026 MCCM 2.0+(23 Variables Ver.): April 12":
            "2026-mccm-2023-variables-ver-april-12",
        "SHI and Caspian Port Dynamics in Iran: April 9–10, 2026":
            "shi-and-caspian-port-dynamics-in-iran-april-9-10-2026",
        "MCCM Daily War Cost Dynamics (K-Line): Feb 28–Apr 3, 2026":
            "mccm-daily-war-cost-dynamics-k-line-feb-28-apr-3-2026",
        "MCCM Daily Direct War Cost by Actor: Feb 28 – Apr 1, 2026":
            "mccm-daily-direct-war-cost-by-actor-feb-28-apr-1-2026",
        "2026 Middle East Conflict Cost Monitor (MCCM)":
            "2026-middle-east-conflict-cost-monitor-mccm",

        # Confirmed / short slugs
        "The Quiet Surge: How AI Procurement Is Reshaping the Logic of War":
            "the-quiet-surge-how-ai-procurement-is-reshaping-the-logic-of-war",
        "The Strategic Misalignment of U.S. Power":
            "the-strategic-misalignment-of-us-power",
        "War as Training Data: Ukraine and the Future of Datafied Conflict":
            "war-as-training-data-ukraine-and-the-future-of-datafied-conflict",
        "Beyond Rankings: What Really Defines AI National Power?":
            "beyond-rankings-what-really-defines-ai-national-power",
        "Why the South?":
            "why-the-south",

        # Long articles where GoDaddy may use only main-title slug
        "When AI Infrastructure Is Optional but Governance Lock-In Is Not":
            "when-ai-infrastructure-is-optional-but-governance-lock-in-is-not",
        "Greenland as a Structural AI Strategic Node: Perception Integrity, Temporal Dominance, and the Arctic Reconfiguration of Algorithmic Power":
            "greenland-as-a-structural-ai-strategic-node",
        "When Decapitation No Longer Matters: AI-Delegated Execution and the Potential Failure of Preemptive Strike Logic":
            "when-decapitation-no-longer-matters",
        "Permanent Presence under Uncertainty: A Partially Observable Game-Theoretic Framework for Unmanned Systems, Cost–Frequency Dynamics, and Strategic Stability":
            "permanent-presence-under-uncertainty",
        "Survivor Governance: Authority Concentration under AI-Driven State Contraction":
            "survivor-governance",
        "Strategic Discontinuity in AI-Enabled Warfare: Machine-Led vs Human-Led OODA":
            "strategic-discontinuity-in-ai-enabled-warfare",
        "Unmanned Algorithmic Warfare and Human Role Reconfiguration: An International Law Perspective":
            "unmanned-algorithmic-warfare-and-human-role-reconfiguration",
        "Single-/Few-Human–AI Firms and Single-/Few-Human–AI–Robot Firms: New Archetypes under the MMC Framework":
            "single-few-human-ai-firms-and-single-few-human-ai-robot-firms",
        "Gray-Zone Maritime Rights-Protection Strategy: Asymmetric Costs and Sustainable Presence, A Case Study of the China–Philippines Dispute over Scarborough Shoal":
            "gray-zone-maritime-rights-protection-strategy",
        "An Analysis of the 2025 India-Pakistan Conflict: From Regional Flashpoint to Global Faultline":
            "an-analysis-of-the-2025-india-pakistan-conflict",

        # Confirmed older publication slugs
        "Artificial Intelligence as National Power: Implications of the 2025 U.S. National Security Strategy for AI Development":
            "artificial-intelligence-as-national-power",
        "From Space Infrastructure to AI State Capacity: South Korea’s National AI Trajectory Analysis Through KASA’s 2026 Strategy":
            "from-space-infrastructure-to-ai-state-capacity",
        "Rethinking the Human–AI Division of Labor: From Irreplaceable Work to Meta-Functional Governance and Coevolution":
            "rethinking-the-human-ai-division-of-labor",
        "Geopolitical Consequences of Cloud Outages: The Systemic Risks of AWS Architecture, National Security, and Digital Sovereignty":
            "geopolitical-consequences-of-cloud-outages",
        "Epistemic Humility in AGI: Toward Ethical & Adaptive Intelligence":
            "epistemic-humility-in-agi-toward-ethical-adaptive-intelligence",
        "Pinocchio or Frankenstein: AGI Frameworks Review and Forward":
            "pinocchio-or-frankenstein-agi-frameworks-review-and-forward",
        "AI: From Information Cocoon to Cognitive Cocoon?":
            "ai-from-information-cocoon-to-cognitive-cocoon",
        "How AI and Corporate Principles Are Reshaping Government?":
            "how-ai-and-corporate-principles-are-reshaping-government",
    }

    rows = []
    for date_value, title in ARTICLE_CATALOG:
        manual_url = get_manual_url_override(title)
        auto_slug = mccm_daily_slug(title)
        slug = manual.get(title) or auto_slug or normalize_slug(title)

        candidate_urls = []
        if manual_url:
            # Manual URL has highest priority and uses skip_strict_title_validation.
            candidate_urls.append(manual_url)

        for sv in slug_variants(slug):
            candidate_urls.extend([
                f"https://epinova.org/articles/f/{sv}",
                f"https://epinova.org/f/{sv}",
                f"https://epinova.org/publications/f/{sv}",
            ])

        # Remove duplicate URLs while preserving order.
        deduped_urls = []
        seen = set()
        for u in candidate_urls:
            if u not in seen:
                seen.add(u)
                deduped_urls.append(u)

        rows.append({
            "date": date_value,
            "title": title,
            "slug": slug,
            "candidate_urls": deduped_urls,
            "manual_url_override": bool(manual_url),
            "manual_url": manual_url or "",
            "skip_strict_title_validation": bool(manual_url),
        })
    return rows


def title_matches_page(expected_title: str, visible_text: str) -> bool:
    """
    Relaxed title validation for GoDaddy pages.

    It tolerates:
    - en dash / hyphen differences;
    - short GoDaddy slugs where only the main title appears;
    - page bodies that do not repeat the full catalog title;
    - title/date inconsistencies such as the March 16 page using a March 15-1 URL.
    """
    expected = normalize_text_for_match(clean_text(expected_title))
    page = normalize_text_for_match(clean_text(visible_text))

    if not expected or not page:
        return False

    if expected in page:
        return True

    if expected[:35] in page:
        return True

    main_title = expected.split(":")[0].strip()
    if len(main_title) >= 10 and main_title in page:
        return True

    compact_expected = compact_text(expected)
    compact_page = compact_text(page)
    if len(compact_expected) >= 20 and compact_expected[:45] in compact_page:
        return True

    stop_words = {
        "through", "between", "framework", "analysis", "toward", "under",
        "with", "from", "into", "and", "the", "for", "of", "in", "on",
        "as", "to", "by", "a", "an", "its", "how", "what", "when",
        "u", "s", "ai", "mccm",
    }
    words = [w for w in re.split(r"[^a-z0-9]+", expected) if len(w) >= 5 and w not in stop_words]
    if not words:
        return False

    hits = sum(1 for w in words if w in page)
    return hits >= min(3, len(words)) or (hits / max(len(words), 1)) >= 0.55


def get_title(soup: BeautifulSoup, fallback: str = "") -> str:
    for tag in [
        soup.find("meta", property="og:title"),
        soup.find("meta", attrs={"name": "twitter:title"}),
    ]:
        if tag and tag.get("content"):
            title = tag["content"]
            title = title.replace("| EPINOVA", "").replace("- EPINOVA", "")
            return clean_text(title)

    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text(" ", strip=True))

    if soup.title:
        title = soup.title.get_text(" ", strip=True)
        title = title.replace("| EPINOVA", "").replace("- EPINOVA", "")
        return clean_text(title)

    return fallback or "Untitled Article"


def get_description(soup: BeautifulSoup) -> str:
    for selector in [
        {"property": "og:description"},
        {"name": "description"},
        {"name": "twitter:description"},
    ]:
        tag = soup.find("meta", selector)
        if tag and tag.get("content"):
            return clean_text(tag["content"])
    return ""


def is_nav_line(line: str) -> bool:
    text = clean_text(line).lower()
    return text in {
        "home", "publications", "articles", "working paper", "working papers",
        "reports", "policy brief", "policy briefs", "white books", "centers",
        "global ai governance", "ai & societal evolution", "ai & emerging tech",
        "ai & human resilience", "maritime history & tech", "showcase", "about us",
        "contact us", "back to top",
    }


def is_stop_line(line: str) -> bool:
    text = clean_text(line).lower()
    stop_keywords = [
        "share this post", "back to top", "copyright ©", "all rights reserved",
        "email:", "phone:", "privacy policy", "terms and conditions", "powered by godaddy",
    ]
    return any(kw in text for kw in stop_keywords)


def extract_article_text_from_visible_text(visible_text: str, expected_title: str) -> str:
    lines = [line.strip() for line in visible_text.splitlines() if line.strip()]
    start = None
    expected = clean_text(expected_title).lower()
    expected_main = expected.split(":")[0].strip()
    expected_short = expected[:35]

    for i, line in enumerate(lines):
        low = clean_text(line).lower()
        if expected_short in low or (len(expected_main) >= 10 and expected_main in low):
            start = i
            break

    if start is None:
        return ""

    kept = []
    for line in lines[start:]:
        if is_stop_line(line):
            break
        if is_nav_line(line):
            continue
        kept.append(line)
    return "\n\n".join(kept)


def remove_noise(node) -> None:
    noise_selectors = [
        "script", "style", "noscript", "iframe", "form", "nav", "footer", "header",
        "[role='navigation']", "[aria-label='Main Navigation']", "[data-aid='HEADER']",
        "[data-aid='FOOTER']", "[data-aid='NAVIGATION']", "[data-aid='SOCIAL_LINKS']",
        "[data-aid='FOOTER_COOKIE_BANNER_RENDERED']", ".cookie", ".cookie-banner",
    ]
    for selector in noise_selectors:
        for tag in node.select(selector):
            tag.decompose()


def extract_article_node(soup: BeautifulSoup, expected_title: str, article_text_reference: str) -> BeautifulSoup:
    """
    Prefer a DOM node so image positions are preserved. If no reliable DOM node is found,
    the caller will fall back to visible-text reconstruction.
    """
    remove_noise(soup)
    reference_len = max(len(clean_text(article_text_reference)), 1)
    candidates = []

    selectors = [
        "article", "main article", "[data-aid='BLOG_POST_PAGE']", "[data-aid='BLOG_POST_CONTENT']",
        "[data-aid='BLOG_CONTENT']", ".blog-post", ".post-content", "main", "[role='main']",
        "section", "div", "body",
    ]

    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if len(text) < 250:
                continue
            if not title_matches_page(expected_title, text):
                continue

            penalty = 0
            bad_phrases = [
                "Home Publications Articles Working Paper",
                "Centers Global AI Governance",
                "About Us Contact US",
                "Privacy Policy Terms and Conditions",
                "This website uses cookies",
            ]
            for phrase in bad_phrases:
                if phrase.lower() in text.lower():
                    penalty += 4000

            length_distance = abs(len(text) - reference_len)
            image_bonus = len(node.find_all("img")) * 250
            score = -length_distance - penalty + image_bonus
            candidates.append((score, node))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    return build_article_html_from_text(soup, article_text_reference)


def build_article_html_from_text(soup: BeautifulSoup, article_text: str):
    article = soup.new_tag("article")
    for block in article_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        p = soup.new_tag("p")
        p.string = block
        article.append(p)
    return article


def image_ext(url: str, content_type: str = "") -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
        return ext
    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
    return guessed or ".jpg"


def extract_img_src(img) -> str:
    src = (
        img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        or img.get("data-srclazy") or ""
    )

    if src.startswith("data:image"):
        src = img.get("data-srclazy") or img.get("data-src") or img.get("data-lazy-src") or ""
        if not src:
            srcset = img.get("data-srcsetlazy") or img.get("data-srcset") or img.get("srcset") or ""
            if srcset:
                src = srcset.split(",")[0].strip().split(" ")[0]
    return src


def download_images(article_node, article_url: str, out_dir: Path) -> list[dict]:
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    image_records = []
    seen = {}
    counter = 1

    for img in article_node.find_all("img"):
        src = extract_img_src(img)
        if not src or src.startswith("data:image"):
            continue

        remote_url = normalize_url(urljoin(article_url, src))
        low = remote_url.lower()
        if any(x in low for x in [
            "transparent_placeholder", "favicon", "logo", "social", "facebook", "twitter",
            "linkedin", "instagram", "pixel", "tracking", "trustedsite", "meter/epinova",
        ]):
            continue

        if remote_url in seen:
            img["src"] = seen[remote_url]
            continue

        try:
            r = requests.get(remote_url, headers=REQUEST_HEADERS, timeout=30)
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            ext = image_ext(remote_url, content_type)
            filename = f"image-{counter:03d}{ext}"
            local_path = assets_dir / filename
            local_rel = f"assets/{filename}"
            local_path.write_bytes(r.content)

            img["src"] = local_rel
            img["alt"] = img.get("alt", "")
            for attr in [
                "srcset", "data-src", "data-srcset", "data-lazy-src", "data-srclazy",
                "data-srcsetlazy", "sizes", "data-lazyimg",
            ]:
                if img.has_attr(attr):
                    del img[attr]

            seen[remote_url] = local_rel
            image_records.append({
                "filename": local_rel,
                "original_url": remote_url,
                "content_type": mimetypes.guess_type(local_rel)[0] or content_type or "image",
                "description": "Locally archived image from the original EPINOVA article."
            })
            counter += 1
        except Exception as exc:
            print(f"Warning: failed to download image: {remote_url} | {exc}")

    return image_records


def html_to_markdown(html: str) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = False
    converter.protect_links = True
    return converter.handle(html).strip()


def build_metadata(
    title: str,
    description: str,
    publication_date: str,
    url: str,
    folder_name: str,
    image_records: list[dict],
) -> dict:
    year = publication_date[:4] if publication_date[:4].isdigit() else "undated"
    epinova_id = f"EPINOVA-ART-{year}-{normalize_slug(title)[:40]}"
    files = [
        {"filename": "article.html", "content_type": "text/html", "description": "Archived HTML copy of the original EPINOVA article, including locally preserved images."},
        {"filename": "article.md", "content_type": "text/markdown", "description": "Markdown preservation copy of the article."},
        {"filename": "article.txt", "content_type": "text/plain", "description": "Plain-text preservation copy of the article."},
    ] + image_records
    citation = f"Wu, Shaoyuan. ({year}). {title}. EPINOVA LLC. {url}"
    return {
        "epinova_id": epinova_id,
        "title": title,
        "full_title": title,
        "subtitle": "",
        "creators": [CREATOR],
        "category": "articles",
        "resource_type": "Text",
        "publication_type": "Article",
        "publication_date": publication_date,
        "version": "v1.0",
        "status": "Archived from EPINOVA GoDaddy blog",
        "language": "en",
        "publisher": PUBLISHER,
        "place": "Carrollton, Georgia, United States",
        "doi": "To be assigned after Crossref registration",
        "previous_doi": "",
        "abstract": description,
        "description": description,
        "keywords": [],
        "subjects": ["AI governance", "Strategic systems analysis", "Technology policy"],
        "license": {"title": "All rights reserved", "url": ""},
        "copyright": f"© {year} EPINOVA LLC. All rights reserved.",
        "recommended_citation": citation,
        "citation_apa": citation,
        "original_page": url,
        "canonical_url": "",
        "source_status": "archived_from_godaddy_blog_with_images",
        "repository_folder": f"Articles/{folder_name}",
        "official_page": url,
        "alternate_identifiers": [{"scheme": "URL", "identifier": url, "description": "Original EPINOVA article page."}],
        "related_works": [],
        "references": [],
        "files": files,
    }


def try_archive_catalog_item(item: dict, order_number: int) -> dict | None:
    expected_date = item["date"]
    expected_title = item["title"]
    last_error = ""

    for idx, candidate_url in enumerate(item["candidate_urls"]):
        try:
            html, visible_text, final_url = render_page(candidate_url)

            is_manual_candidate = bool(item.get("manual_url_override")) and idx == 0 and normalize_url(candidate_url) == normalize_url(item.get("manual_url", ""))
            if is_manual_candidate:
                warning = manual_url_warning(expected_title, candidate_url)
                if warning:
                    print(f"  {warning}")
                print(f"  Manual override URL used; skipped strict title validation: {candidate_url}")
            elif not title_matches_page(expected_title, visible_text):
                last_error = f"title not found in page body at {candidate_url}"
                continue

            soup = BeautifulSoup(html, "html.parser")
            title = get_title(soup, fallback=expected_title)
            if title in {"EIPINOVA", "EPINOVA", "Publications", "Articles"}:
                title = expected_title
            description = get_description(soup)

            article_text_reference = extract_article_text_from_visible_text(visible_text, expected_title)
            if len(article_text_reference) < 250 and is_manual_candidate:
                # Manual short-slug pages may not repeat the exact catalog title.
                # Use a cleaned visible-text fallback rather than failing the page.
                fallback_lines = [line.strip() for line in visible_text.splitlines() if line.strip()]
                kept = []
                for line in fallback_lines:
                    if is_stop_line(line):
                        break
                    if is_nav_line(line):
                        continue
                    kept.append(line)
                article_text_reference = "\n\n".join(kept)

            if len(article_text_reference) < 250:
                last_error = f"too little visible body content at {candidate_url}"
                continue

            article_node = extract_article_node(soup, expected_title, article_text_reference)
            article_text = article_node.get_text("\n", strip=True)
            article_text = "\n".join(line.strip() for line in article_text.splitlines() if line.strip())

            # If DOM extraction is clearly too broad or too short, use visible-text reconstruction.
            if len(article_text) < 250 or len(article_text) > max(2500, len(article_text_reference) * 3):
                article_node = build_article_html_from_text(soup, article_text_reference)
                article_text = article_text_reference

            publication_date = expected_date
            folder_name = f"{publication_date}_{normalize_slug(expected_title)[:80]}"
            out_dir = OUTPUT_DIR / folder_name
            out_dir.mkdir(parents=True, exist_ok=True)

            image_records = download_images(article_node, final_url, out_dir)
            article_html_inner = str(article_node)
            article_md_body = html_to_markdown(article_html_inner)

            archived_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html_escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      max-width: 880px;
      margin: 40px auto;
      padding: 0 24px;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.65;
      color: #222;
    }}
    img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 24px 0;
    }}
    .meta {{
      color: #666;
      font-size: 14px;
      border-bottom: 1px solid #ddd;
      padding-bottom: 16px;
      margin-bottom: 28px;
    }}
  </style>
</head>
<body>
  <h1>{html_escape(title)}</h1>
  <div class="meta">
    <p><strong>Original URL:</strong> <a href="{html_escape(final_url)}">{html_escape(final_url)}</a></p>
    <p><strong>Publication date:</strong> {html_escape(publication_date)}</p>
    <p><strong>Archive note:</strong> This is a locally preserved copy of an EPINOVA article originally generated through the GoDaddy blog system.</p>
  </div>
  {article_html_inner}
</body>
</html>
"""

            article_md = f"""# {title}

Original URL: {final_url}

Publication date: {publication_date}

Archive note: This is a locally preserved Markdown copy of an EPINOVA article originally generated through the GoDaddy blog system.

---

{article_md_body}
"""

            (out_dir / "article.html").write_text(archived_html, encoding="utf-8")
            (out_dir / "article.md").write_text(article_md, encoding="utf-8")
            (out_dir / "article.txt").write_text(article_text, encoding="utf-8")

            metadata = build_metadata(
                title=title,
                description=description,
                publication_date=publication_date,
                url=final_url,
                folder_name=folder_name,
                image_records=image_records,
            )
            (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

            return {
                "title": title,
                "expected_title": expected_title,
                "date": publication_date,
                "url": final_url,
                "folder": str(out_dir),
                "images": len(image_records),
                "status": "archived",
            }
        except Exception as exc:
            last_error = f"{candidate_url} | {exc}"

    print(f"  Failed all URL variants for: {expected_title}")
    print(f"  Last error: {last_error}")
    return {
        "title": expected_title,
        "date": expected_date,
        "url": "",
        "folder": "",
        "images": 0,
        "status": "failed",
        "error": last_error,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog_items = catalog_to_seed_urls()
    print(f"Catalog items: {len(catalog_items)}")
    print(f"Output folder: {OUTPUT_DIR}")

    results = []
    for i, item in enumerate(catalog_items, start=1):
        print(f"[{i}/{len(catalog_items)}] {item['date']} | {item['title']}")
        result = try_archive_catalog_item(item, i)
        if result:
            results.append(result)
        if result and result.get("status") == "archived":
            print(f"  Saved: {result['folder']} | images: {result['images']}")
        else:
            print(f"  Failed: {result.get('error', '') if result else ''}")
        time.sleep(0.8)

    archived = [r for r in results if r.get("status") == "archived"]
    failed = [r for r in results if r.get("status") == "failed"]
    results_sorted = sorted(results, key=lambda r: (r.get("date") or "", r.get("title") or ""), reverse=True)

    index_path = OUTPUT_DIR / "articles_archive_index.json"
    failed_path = OUTPUT_DIR / "articles_failed_index.json"
    index_path.write_text(json.dumps(results_sorted, ensure_ascii=False, indent=2), encoding="utf-8")
    failed_path.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Catalog items: {len(catalog_items)}")
    print(f"Archived: {len(archived)}")
    print(f"Failed: {len(failed)}")
    print(f"Index file: {index_path}")
    print(f"Failed file: {failed_path}")

    if len(archived) < MIN_EXPECTED_ARTICLES:
        print()
        print("WARNING:")
        print(f"Only archived {len(archived)} articles.")
        print(f"Expected at least {MIN_EXPECTED_ARTICLES}.")
        print("Check articles_failed_index.json for missing pages or slug differences.")


if __name__ == "__main__":
    main()
