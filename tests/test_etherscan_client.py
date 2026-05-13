import json
from pathlib import Path
import pytest
import responses
from scripts.utils.etherscan_client import EtherscanClient

FIXTURES = Path(__file__).parent / "fixtures"


@responses.activate
def test_get_logs_parses_response():
    resp = json.loads((FIXTURES / "etherscan_logs_response.json").read_text())
    responses.add(
        responses.GET,
        "https://api.etherscan.io/api",
        json=resp, status=200,
    )
    client = EtherscanClient(api_key="test-key")
    logs = client.get_logs(
        address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        topic0="0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855",
        from_block=0,
        to_block=999999999,
    )
    assert len(logs) == 1
    assert logs[0]["transactionHash"] == "0xdeadbeef"


@responses.activate
def test_get_logs_raises_on_api_error():
    responses.add(
        responses.GET,
        "https://api.etherscan.io/api",
        json={"status": "0", "message": "NOTOK", "result": "Invalid API Key"},
        status=200,
    )
    client = EtherscanClient(api_key="test-key")
    with pytest.raises(RuntimeError, match="Invalid API Key"):
        client.get_logs(
            address="0x0", topic0="0x0", from_block=0, to_block=1,
        )


def test_client_requires_api_key():
    with pytest.raises(ValueError, match="api_key"):
        EtherscanClient(api_key="")


from scripts.utils.etherscan_client import EtherscanError


@responses.activate
def test_etherscan_http_error_wraps_as_etherscan_error():
    """I-1: 5xx surfaces as EtherscanError, not requests.HTTPError."""
    responses.add(
        responses.GET,
        "https://api.etherscan.io/api",
        json={"error": "internal"}, status=502,
    )
    client = EtherscanClient(api_key="test-key")
    with pytest.raises(EtherscanError, match="Etherscan request failed"):
        client.get_logs(address="0x0", topic0="0x0", from_block=0, to_block=1)


@responses.activate
def test_etherscan_raises_on_offset_cap_exceeded():
    """I-3: silent-truncation guard — raise if result count >= offset."""
    # Build a response with exactly 1000 logs (the default offset cap).
    big_logs = [{"transactionHash": f"0x{i:064x}"} for i in range(1000)]
    responses.add(
        responses.GET,
        "https://api.etherscan.io/api",
        json={"status": "1", "message": "OK", "result": big_logs}, status=200,
    )
    client = EtherscanClient(api_key="test-key")
    with pytest.raises(EtherscanError, match="at or above offset cap"):
        client.get_logs(address="0x0", topic0="0x0", from_block=0, to_block=999999999)


def test_etherscan_error_subclasses_runtime_error():
    """I-1: existing RuntimeError-catching tests still work — EtherscanError is a subclass."""
    assert issubclass(EtherscanError, RuntimeError)
