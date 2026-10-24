import pytest

from msaf.prime_integration import certify_prime_conjecture

def test_prime_conjecture_small():
    cert = certify_prime_conjecture(100_000)
    assert isinstance(cert, dict)
    for key in ("schema", "statement", "confidence", "bound"):
        assert key in cert
