#!/usr/bin/env python3
"""Add works that are on ORCID but not yet in _bibliography/papers.bib.

Reads the ORCID iD from _data/socials.yml, lists the public works on the ORCID
record, and for every work whose DOI (or title) is not already in papers.bib,
fetches a BibTeX record from doi.org and inserts it at the top of the file.

Nothing existing is edited or removed, so hand-made tweaks († markers,
`selected`, `additional_info`, ...) are safe. New entries use the publisher's
author formatting; tidy them and add annotations before merging.

Usage:  python bin/orcid_sync.py [--dry-run]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "_bibliography" / "papers.bib"
SOCIALS = ROOT / "_data" / "socials.yml"
MARKER = "% --- entries below this line are maintained by hand; ORCID sync inserts new ones above ---"

# ORCID work types that belong on the publications page.
WANTED_TYPES = {
    "journal-article",
    "book-chapter",
    "book",
    "edited-book",
    "preprint",
    "conference-paper",
    "review",
    "dissertation-thesis",
}
HEADERS = {"User-Agent": "olihammond.github.io ORCID sync (https://github.com/olihammond)"}
TIMEOUT = 30


def norm_doi(doi: str) -> str:
    doi = doi.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi.removeprefix("doi:").strip()


def norm_title(title: str) -> str:
    title = re.sub(r"\\[a-zA-Z]+|[{}$\\]", "", title)  # strip LaTeX
    title = re.sub(r"<[^>]+>", "", title)  # strip HTML/MathML tags
    title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", title.lower())


def ascii_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def existing(bib_text: str) -> tuple[set[str], set[str], set[str]]:
    dois = {norm_doi(d) for d in re.findall(r"^\s*doi\s*=\s*[{\"]+([^}\"]+)", bib_text, re.I | re.M)}
    titles = {norm_title(t) for t in re.findall(r"^\s*title\s*=\s*[{\"]+(.+?)[}\"]+,?\s*$", bib_text, re.I | re.M)}
    keys = set(re.findall(r"^@\w+\{([^,\s]+),", bib_text, re.M))
    return dois, titles, keys


def orcid_works(orcid: str) -> list[dict]:
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    r = requests.get(url, headers={**HEADERS, "Accept": "application/json"}, timeout=TIMEOUT)
    r.raise_for_status()
    works = []
    for group in r.json().get("group") or []:
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        s = summaries[0]  # the user's preferred version of this work
        dois = []
        for src in [group] + summaries:
            for ext in ((src.get("external-ids") or {}).get("external-id")) or []:
                if (ext.get("external-id-type") or "").lower() == "doi" and ext.get("external-id-value"):
                    d = norm_doi(ext["external-id-value"])
                    if d not in dois:
                        dois.append(d)
        works.append(
            {
                "title": (((s.get("title") or {}).get("title") or {}).get("value") or "").strip(),
                "type": s.get("type") or "",
                "year": (((s.get("publication-date") or {}).get("year") or {}).get("value")) or "",
                "journal": ((s.get("journal-title") or {}).get("value")) or "",
                "dois": dois,
            }
        )
    return works


def fetch_bibtex(doi: str) -> str | None:
    try:
        r = requests.get(
            f"https://doi.org/{doi}",
            headers={**HEADERS, "Accept": "application/x-bibtex; charset=utf-8"},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        return None
    if r.status_code != 200 or not r.text.lstrip().startswith("@"):
        return None
    r.encoding = "utf-8"
    return r.text.strip()


def make_key(bibtex: str, work: dict, taken: set[str]) -> str:
    m = re.search(r"author\s*=\s*[{\"]\s*([^,}\"]+?)(?:,|\s+and\s|[}\"])", bibtex, re.I)
    first = m.group(1).strip() if m else "work"
    if "," not in (re.search(r"author\s*=\s*[{\"]([^}\"]*)", bibtex, re.I) or [None, ""])[1].split(" and ")[0]:
        first = first.split()[-1]  # "Oliver S. Hammond" -> "Hammond"
    year = work["year"] or (re.search(r"year\s*=\s*[{\"]?(\d{4})", bibtex, re.I) or [None, "nd"])[1]
    words = [w for w in re.findall(r"[A-Za-z]+", work["title"]) if len(w) > 3]
    base = f"{ascii_slug(first) or 'work'}{year}{ascii_slug(words[0]) if words else ''}"
    key, n = base, 1
    while key in taken:
        n += 1
        key = f"{base}{n}"
    taken.add(key)
    return key


def tidy(bibtex: str, key: str) -> str:
    bibtex = re.sub(r"^(@\w+)\{[^,]*,", rf"\1{{{key},", bibtex.strip(), count=1)
    # doi.org sometimes returns the whole record on one line: put each field on its own line
    if bibtex.count("\n") < 3:
        bibtex = re.sub(r",\s*(\w+)\s*=\s*", r",\n  \1 = ", bibtex)
        bibtex = re.sub(r"\s*\}\s*$", "\n}", bibtex)
    bibtex = re.sub(r"^\s*(url|abstract)\s*=.*,\s*\n", "", bibtex, flags=re.I | re.M)
    return bibtex


def minimal_entry(work: dict, key: str) -> str:
    kind = {"book-chapter": "incollection", "book": "book", "edited-book": "book"}.get(work["type"], "article")
    lines = [f"@{kind}{{{key},", f"  title = {{{{{work['title']}}}}},", "  author = {Hammond, O. S.},"]
    if work["journal"]:
        lines.append(f"  journal = {{{work['journal']}}},")
    if work["year"]:
        lines.append(f"  year = {{{work['year']}}},")
    if work["dois"]:
        lines.append(f"  doi = {{{work['dois'][0]}}},")
    lines.append("  note = {Author list incomplete: imported from ORCID summary}")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="report what would be added without writing")
    args = ap.parse_args()

    orcid = (yaml.safe_load(SOCIALS.read_text(encoding="utf-8")) or {}).get("orcid_id")
    if not orcid:
        print("No orcid_id in _data/socials.yml", file=sys.stderr)
        return 1

    bib_text = BIB.read_text(encoding="utf-8")
    have_dois, have_titles, keys = existing(bib_text)
    works = orcid_works(orcid)
    print(f"ORCID {orcid}: {len(works)} works on record; {len(have_dois)} DOIs already in papers.bib")

    new_entries, skipped = [], []
    for w in works:
        if w["type"] not in WANTED_TYPES:
            continue
        if any(d in have_dois for d in w["dois"]) or (w["title"] and norm_title(w["title"]) in have_titles):
            continue
        if not w["title"] and not w["dois"]:
            continue
        if not w["dois"]:
            skipped.append(f"{w['title']} ({w['year']}) - no DOI on ORCID, add by hand")
            continue
        raw = fetch_bibtex(w["dois"][0])
        key = make_key(raw or "author = {Hammond, O. S.}", w, keys)
        entry = tidy(raw, key) if raw else minimal_entry(w, key)
        new_entries.append(entry)
        have_dois.update(w["dois"])
        have_titles.add(norm_title(w["title"]))
        print(f"  + {key}: {w['title']} ({w['year']})")

    for s in skipped:
        print(f"  ! skipped: {s}")
    if not new_entries:
        print("papers.bib is up to date.")
        return 0
    if args.dry_run:
        print(f"{len(new_entries)} new entr{'y' if len(new_entries) == 1 else 'ies'} (dry run, nothing written).")
        return 0

    block = (
        f"% Added from ORCID on {dt.date.today().isoformat()}: check authors, add † / * markers and `annotation` as needed.\n"
        + "\n\n".join(new_entries)
        + "\n\n"
    )
    if MARKER not in bib_text:
        first = re.search(r"^@", bib_text, re.M)
        pos = first.start() if first else len(bib_text)
        bib_text = bib_text[:pos] + MARKER + "\n\n" + bib_text[pos:]
    bib_text = bib_text.replace(MARKER, block + MARKER, 1)
    BIB.write_text(bib_text, encoding="utf-8")
    print(f"Wrote {len(new_entries)} new entr{'y' if len(new_entries) == 1 else 'ies'} to {BIB.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
