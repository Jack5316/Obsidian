#!/usr/bin/env python3
"""Dictionary - Search Longman Dictionary of Contemporary English (LDOCE) for word meaning, etymology, and corpus examples.

Uses Pearson LDOCE API (no API key required).
"""

import argparse
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests

from config import save_note, VAULT_PATH

PEARSON_API = "https://api.pearson.com/v2/dictionaries"
LDOCE5 = "ldoce5"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "ObsidianVaultBot/1.0",
    "Accept": "application/json",
}


def search_headword(word: str) -> list:
    """Search LDOCE for entries matching headword."""
    url = f"{PEARSON_API}/{LDOCE5}/entries"
    params = {"headword": word.strip()}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Search failed: {e}")
        return []


def fetch_entry(entry_id: str) -> Optional[dict]:
    """Fetch full entry by ID."""
    url = f"{PEARSON_API}/entries/{entry_id}"
    try:
        time.sleep(0.3)  # Be polite to API
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("result")
    except Exception as e:
        print(f"Fetch failed: {e}")
        return None


def pick_best_entry(results: list, word: str) -> Optional[dict]:
    """Pick the best matching entry (prefer exact headword match, skip trademarks)."""
    word_lower = word.strip().lower()
    exact = []
    close = []
    for r in results:
        hw = (r.get("headword") or "").strip()
        if hw.lower() == word_lower:
            exact.append(r)
        elif word_lower in hw.lower():
            close.append(r)
        else:
            close.append(r)
    for r in exact + close:
        hw = (r.get("headword") or "").strip()
        if hw.endswith("!") and "trademark" in str(r.get("senses", [{}])[0].get("definition", "")).lower():
            continue
        return r
    return results[0] if results else None


def format_entry(result: dict, word: str) -> str:
    """Format dictionary entry as markdown."""
    lines = []
    headword = result.get("headword", word)
    lines.append(f"# {headword}\n")
    lines.append(f"*Longman Dictionary of Contemporary English (LDOCE)*\n")

    # Pronunciation
    prons = result.get("pronunciations", [])
    if prons:
        ipa_parts = []
        for p in prons:
            ipa = p.get("ipa", "")
            lang = p.get("lang", "")
            if ipa:
                ipa_parts.append(f"{ipa}" + (f" ({lang})" if lang else ""))
        if ipa_parts:
            lines.append(f"**Pronunciation:** {' | '.join(ipa_parts)}\n")

    # Part of speech
    pos = result.get("part_of_speech", "")
    if pos:
        lines.append(f"**Part of speech:** {pos}\n")

    # Hyphenation
    hyp = result.get("hyphenation", "")
    if hyp:
        lines.append(f"**Hyphenation:** {hyp}\n")

    # Meanings (senses)
    senses = result.get("senses", [])
    if senses:
        lines.append("## Meanings\n")
        for i, s in enumerate(senses, 1):
            defs = s.get("definition", [])
            if isinstance(defs, str):
                defs = [defs]
            for d in defs:
                if d:
                    lines.append(f"{i}. {d}\n")
            exs = s.get("examples", [])
            for ex in exs[:3]:
                text = ex.get("text", "") if isinstance(ex, dict) else str(ex)
                if text:
                    lines.append(f"   - *{text}*\n")
            lex = s.get("lexical_unit", "")
            if lex:
                lines.append(f"   *(lexical unit: {lex})*\n")

    # Etymology / Origin (source)
    etymologies = result.get("etymologies", [])
    if etymologies:
        lines.append("## Etymology (Origin)\n")
        for e in etymologies:
            century = e.get("century", "")
            origin = e.get("origin", "")
            lang = e.get("language") or ""
            if isinstance(lang, list):
                lang = ", ".join(str(x) for x in lang if x)
            parts = []
            if century:
                parts.append(f"**{century}**")
            if origin:
                parts.append(origin)
            if lang:
                parts.append(f"from {lang}")
            if parts:
                lines.append(" ".join(parts) + "\n")

    # Corpus examples (top-level)
    examples = result.get("examples", [])
    if examples:
        lines.append("## Examples from the Corpus\n")
        for ex in examples[:8]:
            text = ex.get("text", "") if isinstance(ex, dict) else str(ex)
            if text:
                lines.append(f"- {text}\n")

    # Variants
    variants = result.get("variants", [])
    if variants:
        lines.append("## Variants\n")
        for v in variants:
            sp = v.get("spelling_variant", "")
            geo = v.get("geography", "")
            if sp:
                lines.append(f"- {sp}" + (f" ({geo})" if geo else "") + "\n")

    # Source URL
    lines.append(f"\n---\n*Source: [LDOCE Online](https://www.ldoceonline.com/dictionary/{quote_plus(word.strip().lower())})*")
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search Longman Dictionary (LDOCE) for meaning, etymology, and corpus examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/dictionary.py hello
  python3 _scripts/dictionary.py "run" --save
  python3 _scripts/dictionary.py etymology --no-save
""",
    )
    parser.add_argument("word", help="Word to look up")
    parser.add_argument("--save", action="store_true", help="Save to vault as Atlas/Dictionary - WORD.md")
    parser.add_argument("--no-save", action="store_true", help="Print only (default)")
    args = parser.parse_args()

    word = args.word.strip()
    if not word:
        print("Please provide a word to look up.")
        return

    print(f"Searching LDOCE for '{word}'...")
    results = search_headword(word)

    if not results:
        print(f"No results found for '{word}'.")
        return

    entry = pick_best_entry(results, word)
    if not entry:
        print("Could not select entry.")
        return

    entry_id = entry.get("id")
    if entry_id:
        full_result = fetch_entry(entry_id)
        if full_result:
            result = full_result
        else:
            result = entry
    else:
        result = entry

    output = format_entry(result, word)
    print(output)

    if args.save:
        safe_word = "".join(c if c.isalnum() or c in " -" else "_" for c in word).strip()
        path = f"Atlas/Dictionary - {safe_word}.md"
        save_note(path, output)
        print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
