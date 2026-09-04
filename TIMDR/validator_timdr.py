"""
TIMDR/validator_timdr.py

Sprawdza ciagłość podstawowych pól finansowych (patrz map.json).

NAPRAWA (ta sesja): domyślna ścieżka do schematu była na sztywno
"GSF/TIMDR/map.json" -- działało to tylko, gdy skrypt jest odpalany z
katalogu NADRZĘDNEGO wobec repo GSF. Teraz ścieżka jest liczona
względem lokalizacji tego pliku (Path(__file__).parent), więc działa
niezależnie od bieżącego katalogu roboczego.

NAZEWNICTWO (ta sesja): pole "commodity_prices" zmienione na
"commodities" -- ujednolicone z GIA/gia_map.json (miało własne
"commodity_index") i FIELDCORE/fieldcore_map.json (miało "commodities"
jako klucz influence_matrix). Wcześniej trzy schematy używały trzech
różnych nazw dla tego samego pojęcia (surowce), więc dane wejściowe do
validate_gsf() musiałyby nosić wszystkie trzy klucze naraz, żeby żaden
moduł nie zgłosił brakującego pola. Teraz wystarczy jeden klucz
"commodities".
"""
import json
from pathlib import Path

_DEFAULT_SCHEMA = Path(__file__).parent / "map.json"


def validate_timdr_continuity(data, schema_path=None):
    path = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    problems = []

    # bardzo uproszczone: sprawdzamy, czy pola w ogole istnieja
    for field in schema["fields"]:
        if field not in data:
            problems.append(
                f"Brakuje pola '{field}' — ciągłość informacji finansowej jest przerwana."
            )

    return {
        "status": "ok" if not problems else "warning",
        "problems": problems or ["Ciągłość podstawowych pól wygląda na zachowaną."],
    }
