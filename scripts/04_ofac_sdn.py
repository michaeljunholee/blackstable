#!/usr/bin/env python3
"""OFAC SDN cross-reference for blacklisted addresses.

Two steps, both reproducible from the raw SDN_ADVANCED.XML publication:

  --extract   Parse every "Digital Currency Address - *" feature in the SDN
              advanced XML into a flat CSV (one row per address) with the
              owning party's name, type, sanctions programs and listing date.
  --match     Join those addresses against data/actions.csv (BLACKLIST and
              UNBLACKLIST targets) and write one row per matching action.

Outputs are written next to the XML under data/raw/ofac_sdn/ and suffixed
with the list's DateOfIssue so successive snapshots never overwrite each
other (e.g. ofac_crypto_addresses_2026-08-20.csv).

Fetch the XML with:
  curl -L -A "Mozilla/5.0" -o data/raw/ofac_sdn/sdn_advanced_<YYYY-MM-DD>.xml \\
    https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).parent
_NS = "{https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ADVANCED_XML}"
_EVM_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {c: i for i, c in enumerate(_B58_ALPHABET)}


def tron_to_evm(address: str) -> str | None:
    """Return the 0x-hex EVM form of a TRON base58check address, or None.

    A TRON address is base58check(0x41 || 20-byte key hash); the same 20 bytes
    are the account's address on every EVM chain. OFAC frequently lists only
    the TRON form (as "Digital Currency Address - TRX" or "- USDT"), so a
    hex-only comparison misses designated keys that Circle blacklists on EVM.
    Returns None for anything that is not a checksum-valid 0x41-prefixed
    TRON address.
    """
    if not address or address[0] != "T" or len(address) != 34:
        return None
    n = 0
    for ch in address:
        idx = _B58_INDEX.get(ch)
        if idx is None:
            return None
        n = n * 58 + idx
    raw = n.to_bytes(25, "big")
    payload, checksum = raw[:21], raw[21:]
    if payload[0] != 0x41:
        return None
    if hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4] != checksum:
        return None
    return "0x" + payload[1:].hex()


def evm_key_for(address: str) -> str:
    """Normalised EVM key for an SDN identifier: hex addresses lower-cased,
    TRON addresses decoded; empty string for non-EVM-compatible identifiers."""
    if _EVM_ADDRESS_RE.match(address):
        return address.lower()
    return tron_to_evm(address) or ""


def _strip(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def _date_text(date_el: ET.Element | None) -> str:
    if date_el is None:
        return ""
    parts = {_strip(c.tag): (c.text or "").strip() for c in date_el}
    try:
        return f"{int(parts['Year']):04d}-{int(parts['Month']):02d}-{int(parts['Day']):02d}"
    except (KeyError, ValueError):
        return ""


def extract_crypto_addresses(xml_path: Path) -> tuple[pd.DataFrame, str]:
    """Return (addresses DataFrame, list DateOfIssue) from an SDN_ADVANCED.XML.

    Streams the file with iterparse so the ~125 MB publication never has to be
    held in memory as a full tree.
    """
    feature_types: dict[str, str] = {}      # FeatureTypeID -> label
    party_subtypes: dict[str, str] = {}     # PartySubTypeID -> label
    sanctions_types: dict[str, str] = {}    # SanctionsTypeID -> label
    parties: dict[str, dict] = {}           # FixedRef -> {name, type, addresses:[(symbol, addr)]}
    entries: dict[str, dict] = {}           # ProfileID -> {listing_date, programs}
    date_of_issue = ""

    for _event, el in ET.iterparse(str(xml_path), events=("end",)):
        tag = _strip(el.tag)
        if tag == "DateOfIssue":
            date_of_issue = _date_text(el)
        elif tag == "FeatureType":
            feature_types[el.get("ID", "")] = (el.text or "").strip()
        elif tag == "PartySubType":
            party_subtypes[el.get("ID", "")] = (el.text or "").strip()
        elif tag == "SanctionsType":
            sanctions_types[el.get("ID", "")] = (el.text or "").strip()
        elif tag == "DistinctParty":
            fixed_ref = el.get("FixedRef", "")
            profile = el.find(f"{_NS}Profile")
            name, ptype, addresses = "", "", []
            if profile is not None:
                ptype = party_subtypes.get(profile.get("PartySubTypeID", ""), "")
                for identity in profile.findall(f"{_NS}Identity"):
                    for alias in identity.findall(f"{_NS}Alias"):
                        if alias.get("Primary") == "true":
                            parts = [
                                (npv.text or "").strip()
                                for npv in alias.iter(f"{_NS}NamePartValue")
                            ]
                            name = " ".join(p for p in parts if p)
                for feature in profile.findall(f"{_NS}Feature"):
                    label = feature_types.get(feature.get("FeatureTypeID", ""), "")
                    if not label.startswith("Digital Currency Address"):
                        continue
                    for detail in feature.iter(f"{_NS}VersionDetail"):
                        addr = (detail.text or "").strip()
                        if addr:
                            addresses.append((label, addr))
            if addresses:
                parties[fixed_ref] = {"name": name, "type": ptype, "addresses": addresses}
            el.clear()
        elif tag == "SanctionsEntry":
            profile_id = el.get("ProfileID", "")
            dates = [
                _date_text(ev.find(f"{_NS}Date")) for ev in el.findall(f"{_NS}EntryEvent")
            ]
            dates = [d for d in dates if d]
            programs = []
            for measure in el.findall(f"{_NS}SanctionsMeasure"):
                if sanctions_types.get(measure.get("SanctionsTypeID", "")) == "Program":
                    comment = measure.find(f"{_NS}Comment")
                    if comment is not None and (comment.text or "").strip():
                        programs.append(comment.text.strip())
            entries[profile_id] = {
                "listing_date": min(dates) if dates else "",
                "programs": "; ".join(sorted(set(programs))),
            }
            el.clear()

    rows = []
    for ref, party in parties.items():
        entry = entries.get(ref, {})
        for symbol, addr in party["addresses"]:
            rows.append({
                "symbol": symbol,
                "address": addr,
                "evm_key": evm_key_for(addr),
                "party_ref": ref,
                "party_name": party["name"],
                "party_type": party["type"],
                "programs": entry.get("programs", ""),
                "listing_date": entry.get("listing_date", ""),
            })
    cols = ["symbol", "address", "evm_key", "party_ref", "party_name", "party_type", "programs", "listing_date"]
    return pd.DataFrame(rows, columns=cols), date_of_issue


def match_actions(addresses: pd.DataFrame, data_dir: Path, issuer: str = "Circle") -> pd.DataFrame:
    """Return one row per (action, SDN address) pair whose EVM address matches.

    Matching is on the normalised 20-byte key: 0x-hex identifiers lower-cased
    and TRON base58 identifiers decoded (see tron_to_evm), independent of the
    digital-currency symbol OFAC filed the identifier under. `match_basis`
    records which form the SDN carried.
    """
    actions = pd.read_csv(data_dir / "actions.csv", dtype=str, keep_default_na=False)
    impls = pd.read_csv(data_dir / "implementations.csv", dtype=str, keep_default_na=False)
    actions = actions[(actions["issuer"] == issuer) & (actions["target_type"] == "ADDRESS")]
    merged = actions.merge(
        impls[["implementation_id", "chain", "block_number"]], on="implementation_id", how="left"
    )
    merged["_key"] = merged["target_identifier"].str.lower()

    evm = addresses[addresses["evm_key"] != ""].copy()
    evm["_key"] = evm["evm_key"]
    evm["match_basis"] = evm["address"].str.match(_EVM_ADDRESS_RE.pattern).map(
        {True: "HEX_IDENTIFIER", False: "TRON_KEY_EQUIVALENCE"}
    )
    # One SDN identifier per (key, party, basis); a key listed both as hex and as
    # TRON for the same party collapses to the hex row.
    evm = evm.sort_values("match_basis").drop_duplicates(subset=["_key", "party_ref"])

    out = merged.merge(evm, on="_key", how="inner")
    out = out.rename(columns={
        "party_name": "ofac_party_name",
        "party_ref": "ofac_party_ref",
        "symbol": "ofac_symbol",
        "address": "ofac_listed_address",
        "programs": "ofac_programs",
        "listing_date": "ofac_listing_date",
        "party_type": "ofac_party_type",
    })
    cols = [
        "action_id", "action_date", "mechanism_type", "target_identifier", "chain", "block_number",
        "ofac_party_name", "ofac_party_ref", "ofac_symbol", "ofac_listed_address", "match_basis",
        "ofac_party_type", "ofac_programs", "ofac_listing_date",
    ]
    return out[cols].sort_values(["action_id", "ofac_party_ref"]).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--xml", required=True, help="path to a dated SDN_ADVANCED.XML snapshot, e.g. data/raw/ofac_sdn/sdn_advanced_2026-08-20.xml")
    parser.add_argument("--extract", action="store_true", help="write ofac_crypto_addresses_<date>.csv")
    parser.add_argument("--match", action="store_true", help="write ofac_matches_<date>.csv")
    parser.add_argument("--issuer", default="Circle")
    args = parser.parse_args()
    if not (args.extract or args.match):
        parser.error("nothing to do: pass --extract and/or --match")

    xml_path = Path(args.xml)
    out_dir = xml_path.parent
    data_dir = _HERE.parent / "data"

    print(f"[ofac] parsing {xml_path} ...", file=sys.stderr)
    addresses, list_date = extract_crypto_addresses(xml_path)
    print(f"[ofac] list date {list_date}: {len(addresses)} digital-currency addresses "
          f"across {addresses['party_ref'].nunique()} parties", file=sys.stderr)

    if args.extract:
        p = out_dir / f"ofac_crypto_addresses_{list_date}.csv"
        addresses.to_csv(p, index=False)
        print(f"[ofac] wrote {p}", file=sys.stderr)
    if args.match:
        matches = match_actions(addresses, data_dir, issuer=args.issuer)
        p = out_dir / f"ofac_matches_{list_date}.csv"
        matches.to_csv(p, index=False)
        print(f"[ofac] {len(matches)} action↔SDN matches "
              f"({matches['action_id'].nunique()} actions) → {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
