# PRZENIESIONE (ta sesja) do GSF/core_nodes/ -- "CORE-NODES" z myslnikiem
# nie jest poprawna nazwa pakietu Pythona (myslnik = operator odejmowania),
# co lamalo `from GSF.CORE-NODES.core_nodes import ...` w VALIDATOR/validator.py
# (SyntaxError). Ten plik zostal zostawiony tu tylko dlatego, ze nie da sie
# go usunac bez dostepu do sandboxa bash w tej sesji -- USUN GO RECZNIE i
# uzywaj GSF/core_nodes/core_nodes.py.
import json

def load_core_nodes(schema_path="GSF/CORE-NODES/nodes.json"):
    with open(schema_path, "r") as f:
        return json.load(f)

def analyze_node(node_data):
    strengths = node_data["strengths"]
    weaknesses = node_data["weaknesses"]

    return {
        "status": "ok",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "hint": "Rdzeń pola zmapowany — tensor może zostać zdeformowany zgodnie z FIELDCORE."
    }
