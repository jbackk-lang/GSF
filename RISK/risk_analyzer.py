"""
RISK/risk_analyzer.py

Skleja wymiary ryzyka (timdr_breaks/gia_overload/fieldcore_tension/
core_nodes_weakness, patrz risk_map.json) z raportu struktury.

NAPRAWA (ta sesja): domyślna ścieżka do schematu liczona teraz względem
lokalizacji tego pliku, nie względem cwd. Logika samej funkcji nie
zmieniła się -- problem NIE był tutaj: był w tym, że VALIDATOR nigdy
nie budował `structure_report` z kluczami pasującymi do `dimensions`
poniżej (klucze się nie zgadzały, więc wszystko wychodziło "unknown").
To jest teraz naprawione w VALIDATOR/validator.py.
"""
import json
from pathlib import Path

_DEFAULT_SCHEMA = Path(__file__).parent / "risk_map.json"


def analyze_risk(structure_report, schema_path=None):
    path = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    dims = schema["dimensions"]

    # zakladamy, ze structure_report ma juz zebrane info z VALIDATORA
    risk = {}

    for dim in dims:
        risk[dim] = structure_report.get(dim, "unknown")

    return {
        "status": "ok",
        "risk_profile": risk,
        "hint": "Ryzyko systemowe ocenione na podstawie struktury pola GSF.",
    }
