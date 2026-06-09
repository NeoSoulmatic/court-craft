"""Ingest NBA transactions from Basketball Reference season pages."""

import hashlib
import re
import time
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup, Comment
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction

DATE_RE = re.compile(r"^[A-Z][a-z]+ \d{1,2}, \d{4}$")
BBREF_HEADERS = {"User-Agent": "CourtCraft/0.1 (educational project; contact via GitHub)"}


def season_to_bbref_slug(season: str) -> str:
    """Map '2024-25' -> 'NBA_2025' (BBRef uses end year)."""
    start, end = season.split("-")
    end_year = int(end) if len(end) == 4 else int(f"{start[:2]}{end}")
    return f"NBA_{end_year}"


def classify_transaction(text: str) -> str:
    lower = text.lower()
    if "traded" in lower or "3-team trade" in lower:
        return "trade"
    if "signed" in lower or "re-signed" in lower or "contract extension" in lower:
        return "signing"
    if "waived" in lower:
        return "waiver"
    if "claimed" in lower:
        return "claim"
    if "retired" in lower or "retirement" in lower:
        return "retirement"
    if any(word in lower for word in ("hired", "fired", "resigns", "resigned", "head coach")):
        return "coaching"
    if "drafted" in lower:
        return "draft"
    return "other"


def _dedup_key(transaction_date: date, description: str) -> str:
    raw = f"{transaction_date.isoformat()}|{description.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _parse_season_page(html: str, season: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.replace_with(BeautifulSoup(comment, "lxml"))

    records: list[dict] = []
    current_date = None

    for element in soup.find_all(["span", "p"]):
        text = element.get_text(" ", strip=True)
        if not text:
            continue

        if DATE_RE.fullmatch(text):
            current_date = datetime.strptime(text, "%B %d, %Y").date()
            continue

        if current_date is None or element.name != "p":
            continue
        if len(text) < 15:
            continue
        if not (text.startswith("The ") or text.startswith("In a") or "announced" in text):
            continue

        records.append(
            {
                "transaction_date": current_date,
                "season": season,
                "transaction_type": classify_transaction(text),
                "description": text,
                "dedup_key": _dedup_key(current_date, text),
            }
        )

    return records


def ingest_season_transactions(session: Session, season: str) -> int:
    slug = season_to_bbref_slug(season)
    url = f"https://www.basketball-reference.com/leagues/{slug}_transactions.html"
    response = requests.get(url, headers=BBREF_HEADERS, timeout=45)
    response.raise_for_status()
    time.sleep(1.0)

    records = _parse_season_page(response.text, season)
    count = 0

    for record in records:
        existing = session.execute(
            select(Transaction).where(Transaction.dedup_key == record["dedup_key"])
        ).scalars().first()
        if existing:
            continue
        session.add(Transaction(source="basketball-reference", **record))
        count += 1

    session.commit()
    return count


def ingest_transactions(session: Session, seasons: list[str]) -> int:
    total = 0
    for season in seasons:
        total += ingest_season_transactions(session, season)
    return total
