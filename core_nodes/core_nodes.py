"""
core_nodes/core_nodes.py

Analiza rdzeni pola finansowego (USA, UE, Chiny -- patrz nodes.json).

NAPRAWA (ta sesja), NAJWAZNIEJSZA W CALYM REPO: ten modul zyl wczesniej
w katalogu "CORE-NODES" (z myslnikiem). Myslnik w Pythonie to operator
odejmowania, wiec `from GSF.CORE-NODES.core_nodes import ...` w
VALIDATOR/validator.py bylo parsowane jako `GSF.CORE - NODES.core_nodes`
-- SyntaxError, natychmiast przy parsowaniu pliku. VALIDATOR nigdy nie
mogl sie uruchomic. Katalog zostal przeniesiony tutaj, do "core_nodes"
(poprawna nazwa pakietu Pythona) -- stary katalog GSF/CORE-NODES/
zostal tylko oznaczony jako przeniesiony (nie dalo sie go usunac w tej
sesji, brak dostepu do sandboxa bash) -- usun go recznie.

Dodatkowo (ta sesja): (1) domyslna sciezka do schematu liczona wzgledem
lokalizacji tego pliku, nie wzgledem cwd. (2) `analyze_node` uzywa
teraz `.get()` zamiast `[]` -- brakujacy klucz w nodes.json daje
czytelny "problem" w wyniku zamiast KeyError, spojnie z reszta modulow
(TIMDR/FIELDCORE zawsze zbieraja liste problemow zamiast sie wywalac).
"""
import json
from pathlib import Path

_DEFAULT_SCHEMA = Path(__file__).parent / "nodes.json"


def load_core_nodes(schema_path=None):
    path = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_node(node_data):
    strengths = node_data.get("strengths", [])
    weaknesses = node_data.get("weaknesses", [])

    problems = []
    if not strengths:
        problems.append("Brak zdefiniowanych 'strengths' dla tego węzła.")
    if not weaknesses:
        problems.append("Brak zdefiniowanych 'weaknesses' dla tego węzła.")

    return {
        "status": "ok" if not problems else "warning",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "problems": problems,
        "hint": (
            "Rdzeń pola zmapowany — tensor może zostać zdeformowany zgodnie z FIELDCORE."
            if not problems
            else "Rdzeń pola zmapowany, ale brakuje części danych — patrz 'problems'."
        ),
    }
