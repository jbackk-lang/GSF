"""
tests/test_validator_smoke.py

Smoke test dla VALIDATOR/validator.py -- glownie po to, zeby zlapac
dokladnie ten typ bledu, ktory istnial w tym repo przed ta sesja: zly
import (SyntaxError) uniemozliwial jakiekolwiek uruchomienie
validate_gsf(). Test importu SAM W SOBIE jest tu najwazniejszy --
gdyby istnial wczesniej, blad #1 z audytu bylby zlapany natychmiast.

Dane w KOMPLETNY_MODEL ponizej sa dobrane recznie tak, zeby pokryc
wszystkie pola z TIMDR/map.json, FIELDCORE/fieldcore_map.json i
GIA/gia_map.json rownoczesnie -- oczekiwany wynik to "stable" (zero
brakujacych pol w TIMDR i FIELDCORE).

UWAGA: ten plik NIE zostal uruchomiony w tej sesji (sandbox bash
niedostepny). Uruchom `pytest tests/ -v` z katalogu GSF/.
"""
import pytest

from GSF.VALIDATOR.validator import validate_gsf

KOMPLETNY_MODEL = {
    # TIMDR/map.json -> fields (i GIA/gia_map.json -> core_fields, ten
    # sam klucz "commodities" po ujednoliceniu nazewnictwa -- patrz
    # naglowek modulow TIMDR/GIA)
    "public_debt": 1.0,
    "interest_rates": 0.05,
    "capital_flows": 100.0,
    "fx_rates": 1.1,
    "commodities": 80.0,
    # FIELDCORE/fieldcore_map.json -> influence_matrix keys
    "capital": 1.0,
    "fx": 1.1,
    "trade": 1.0,
}


def test_import_does_not_raise():
    # Sam ten test jest najwazniejszy w calym pliku -- patrz docstring.
    from GSF.VALIDATOR import validator  # noqa: F401


def test_complete_model_is_stable():
    result = validate_gsf(KOMPLETNY_MODEL)
    assert result["timdr"]["status"] == "ok"
    assert result["fieldcore"]["status"] == "ok"
    assert result["level"] == "stable"


def test_fieldcore_market_breakdown_has_all_four_markets():
    result = validate_gsf(KOMPLETNY_MODEL)
    markets = result["fieldcore"]["markets"]
    assert set(markets.keys()) == {"capital", "fx", "trade", "commodities"}
    for market_info in markets.values():
        assert market_info["status"] == "ok"


def test_missing_data_marks_market_as_missing_and_raises_level():
    # brak "fx" -> ten rynek powinien byc "missing_data", TIMDR nadal ok
    # (fx nie jest w TIMDR/map.json), wiec level == "stressed" (1 z 2
    # wymiarow ma problem -- patrz UWAGA O ZAKRESIE w validator.py)
    model = dict(KOMPLETNY_MODEL)
    del model["fx"]
    result = validate_gsf(model)
    assert result["fieldcore"]["markets"]["fx"]["status"] == "missing_data"
    assert result["fieldcore"]["status"] == "warning"
    assert result["level"] == "stressed"


def test_empty_model_is_critical():
    result = validate_gsf({})
    assert result["timdr"]["status"] == "warning"
    assert result["fieldcore"]["status"] == "warning"
    assert result["level"] == "critical"


def test_risk_profile_keys_match_risk_map_dimensions():
    result = validate_gsf(KOMPLETNY_MODEL)
    assert set(result["risk"]["risk_profile"].keys()) == {
        "timdr_breaks",
        "gia_overload",
        "fieldcore_tension",
        "core_nodes_weakness",
    }
    # wczesniej (przed naprawa) te klucze sie nie zgadzaly z tym, co
    # zwracal validate_gsf(), wiec kazdy wymiar wychodzil "unknown"
    assert "unknown" not in result["risk"]["risk_profile"].values()
