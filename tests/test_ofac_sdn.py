import importlib.util
from pathlib import Path

import pandas as pd

_PATH = Path(__file__).parent.parent / "scripts" / "04_ofac_sdn.py"
_spec = importlib.util.spec_from_file_location("ofac_sdn", _PATH)
ofac_sdn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ofac_sdn)

_NS = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ADVANCED_XML"

_XML = f"""<?xml version="1.0" encoding="utf-8"?>
<Sanctions xmlns="{_NS}" Version="3">
  <DateOfIssue CalendarTypeID="1"><Year>2026</Year><Month>8</Month><Day>20</Day></DateOfIssue>
  <ReferenceValueSets>
    <FeatureTypeValues>
      <FeatureType ID="25">Location</FeatureType>
      <FeatureType ID="345">Digital Currency Address - ETH</FeatureType>
      <FeatureType ID="887">Digital Currency Address - USDT</FeatureType>
    </FeatureTypeValues>
    <PartySubTypeValues>
      <PartySubType ID="3">Entity</PartySubType>
      <PartySubType ID="4">Individual</PartySubType>
    </PartySubTypeValues>
    <SanctionsTypeValues>
      <SanctionsType ID="1705">Block</SanctionsType>
      <SanctionsType ID="1">Program</SanctionsType>
    </SanctionsTypeValues>
  </ReferenceValueSets>
  <DistinctParties>
    <DistinctParty FixedRef="900">
      <Profile ID="900" PartySubTypeID="4">
        <Identity ID="9001" FixedRef="900" Primary="true">
          <Alias FixedRef="900" AliasTypeID="1400" Primary="false">
            <DocumentedName ID="1"><DocumentedNamePart><NamePartValue>ALIAS</NamePartValue></DocumentedNamePart></DocumentedName>
          </Alias>
          <Alias FixedRef="900" AliasTypeID="1403" Primary="true">
            <DocumentedName ID="2">
              <DocumentedNamePart><NamePartValue>KIM</NamePartValue></DocumentedNamePart>
              <DocumentedNamePart><NamePartValue>Example</NamePartValue></DocumentedNamePart>
            </DocumentedName>
          </Alias>
        </Identity>
        <Feature ID="1" FeatureTypeID="25"><FeatureVersion ID="1"><VersionLocation LocationID="1"/></FeatureVersion></Feature>
        <Feature ID="2" FeatureTypeID="345"><FeatureVersion ID="2"><VersionDetail>0xABCDEFabcdef0000000000000000000000000001</VersionDetail></FeatureVersion></Feature>
        <Feature ID="3" FeatureTypeID="887"><FeatureVersion ID="3"><VersionDetail>TXyz123</VersionDetail></FeatureVersion></Feature>
      </Profile>
    </DistinctParty>
    <DistinctParty FixedRef="901">
      <Profile ID="901" PartySubTypeID="3">
        <Identity ID="9011" FixedRef="901" Primary="true">
          <Alias FixedRef="901" AliasTypeID="1403" Primary="true">
            <DocumentedName ID="3"><DocumentedNamePart><NamePartValue>NO CRYPTO CORP</NamePartValue></DocumentedNamePart></DocumentedName>
          </Alias>
        </Identity>
      </Profile>
    </DistinctParty>
  </DistinctParties>
  <SanctionsEntries>
    <SanctionsEntry ID="900" ProfileID="900" ListID="1550">
      <EntryEvent ID="1" EntryEventTypeID="1"><Date CalendarTypeID="1"><Year>2026</Year><Month>7</Month><Day>1</Day></Date></EntryEvent>
      <SanctionsMeasure ID="1" SanctionsTypeID="1705"/>
      <SanctionsMeasure ID="2" SanctionsTypeID="1"><Comment>DPRK3</Comment></SanctionsMeasure>
      <SanctionsMeasure ID="3" SanctionsTypeID="1"><Comment>CYBER2</Comment></SanctionsMeasure>
    </SanctionsEntry>
  </SanctionsEntries>
</Sanctions>
"""


def _write_xml(tmp_path):
    p = tmp_path / "sdn.xml"
    p.write_text(_XML)
    return p


def test_extract_returns_one_row_per_address_with_party_metadata(tmp_path):
    df, list_date = ofac_sdn.extract_crypto_addresses(_write_xml(tmp_path))
    assert list_date == "2026-08-20"
    assert len(df) == 2  # ETH + USDT features; the Location feature and the crypto-less party are skipped
    eth = df[df["symbol"] == "Digital Currency Address - ETH"].iloc[0]
    assert eth["address"] == "0xABCDEFabcdef0000000000000000000000000001"
    assert eth["party_ref"] == "900"
    assert eth["party_name"] == "KIM Example"
    assert eth["party_type"] == "Individual"
    assert eth["programs"] == "CYBER2; DPRK3"
    assert eth["listing_date"] == "2026-07-01"


def test_match_actions_joins_on_lowercased_evm_address(tmp_path):
    df, _ = ofac_sdn.extract_crypto_addresses(_write_xml(tmp_path))
    data_dir = tmp_path / "data"; data_dir.mkdir()
    pd.DataFrame([
        {"action_id": "CU-ACT-0001", "action_date": "2026-07-01", "mechanism_type": "BLACKLIST",
         "target_identifier": "0xabcdefabcdef0000000000000000000000000001", "target_type": "ADDRESS",
         "implementation_id": "CU-IMP-0001", "issuer": "Circle"},
        {"action_id": "CU-ACT-0002", "action_date": "2026-07-01", "mechanism_type": "BLACKLIST",
         "target_identifier": "0x" + "9" * 40, "target_type": "ADDRESS",
         "implementation_id": "CU-IMP-0002", "issuer": "Circle"},
        {"action_id": "CU-ACT-0003", "action_date": "2026-07-01", "mechanism_type": "BLACKLIST",
         "target_identifier": "0xabcdefabcdef0000000000000000000000000001", "target_type": "ADDRESS",
         "implementation_id": "CU-IMP-0003", "issuer": "Tether"},
    ]).to_csv(data_dir / "actions.csv", index=False)
    pd.DataFrame([
        {"implementation_id": "CU-IMP-0001", "chain": "ethereum", "block_number": "1"},
        {"implementation_id": "CU-IMP-0002", "chain": "base", "block_number": "2"},
        {"implementation_id": "CU-IMP-0003", "chain": "ethereum", "block_number": "3"},
    ]).to_csv(data_dir / "implementations.csv", index=False)

    m = ofac_sdn.match_actions(df, data_dir, issuer="Circle")

    assert m["action_id"].tolist() == ["CU-ACT-0001"]
    row = m.iloc[0]
    assert row["ofac_party_name"] == "KIM Example"
    assert row["ofac_programs"] == "CYBER2; DPRK3"
    assert row["ofac_listing_date"] == "2026-07-01"
    assert row["chain"] == "ethereum"


# ---------------------------------------------------------------------------
# TRON ↔ EVM key equivalence: a TRON address is base58check(0x41 + 20-byte key).
# OFAC often lists only the TRX form; Circle blacklists the same key on EVM.
# ---------------------------------------------------------------------------

def test_tron_to_evm_decodes_known_pairs():
    # Pairs from OFAC's 2026-07-01 ISIL Khorasan update, cross-checked on chain.
    assert ofac_sdn.tron_to_evm("TUoixKFaWVsHxGWgnYyMzpkrT22YqU7VvH") == "0xce9f3bc87000393f625088ed40280a74682396cf"
    assert ofac_sdn.tron_to_evm("TA3rH2A7iHnm6pKH8gr9cK1EZnShnmZdFg") == "0x00e0c79525c9f846ee27f8ecf3dcfebb3a335dc7"


def test_tron_to_evm_rejects_bad_checksum_and_non_tron():
    assert ofac_sdn.tron_to_evm("TUoixKFaWVsHxGWgnYyMzpkrT22YqU7VvG") is None  # last char altered
    assert ofac_sdn.tron_to_evm("0xce9f3bc87000393f625088ed40280a74682396cf") is None
    assert ofac_sdn.tron_to_evm("bc1qexample") is None


def test_extract_adds_evm_key_for_tron_addresses(tmp_path):
    xml = _XML.replace("<VersionDetail>TXyz123</VersionDetail>", "<VersionDetail>TUoixKFaWVsHxGWgnYyMzpkrT22YqU7VvH</VersionDetail>")
    p = tmp_path / "sdn.xml"; p.write_text(xml)
    df, _ = ofac_sdn.extract_crypto_addresses(p)
    trx = df[df["symbol"] == "Digital Currency Address - USDT"].iloc[0]
    assert trx["evm_key"] == "0xce9f3bc87000393f625088ed40280a74682396cf"
    eth = df[df["symbol"] == "Digital Currency Address - ETH"].iloc[0]
    assert eth["evm_key"] == "0xabcdefabcdef0000000000000000000000000001"


def test_match_actions_matches_tron_listed_key(tmp_path):
    xml = _XML.replace("<VersionDetail>TXyz123</VersionDetail>", "<VersionDetail>TUoixKFaWVsHxGWgnYyMzpkrT22YqU7VvH</VersionDetail>")
    p = tmp_path / "sdn.xml"; p.write_text(xml)
    df, _ = ofac_sdn.extract_crypto_addresses(p)
    data_dir = tmp_path / "data"; data_dir.mkdir()
    pd.DataFrame([{"action_id": "CU-ACT-0001", "action_date": "2026-07-01", "mechanism_type": "BLACKLIST",
                   "target_identifier": "0xce9f3bc87000393f625088ed40280a74682396cf", "target_type": "ADDRESS",
                   "implementation_id": "CU-IMP-0001", "issuer": "Circle"}]).to_csv(data_dir / "actions.csv", index=False)
    pd.DataFrame([{"implementation_id": "CU-IMP-0001", "chain": "ethereum", "block_number": "1"}]).to_csv(data_dir / "implementations.csv", index=False)
    m = ofac_sdn.match_actions(df, data_dir)
    assert m["action_id"].tolist() == ["CU-ACT-0001"]
    assert m.iloc[0]["ofac_symbol"] == "Digital Currency Address - USDT"
    assert m.iloc[0]["ofac_listed_address"] == "TUoixKFaWVsHxGWgnYyMzpkrT22YqU7VvH"
    assert m.iloc[0]["match_basis"] == "TRON_KEY_EQUIVALENCE"
