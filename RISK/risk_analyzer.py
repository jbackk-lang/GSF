import json

def analyze_risk(structure_report, schema_path="GSF/RISK/risk_map.json"):
    with open(schema_path, "r") as f:
        schema = json.load(f)

    dims = schema["dimensions"]

    # zakładamy, że structure_report ma już zebrane info z VALIDATORA
    risk = {}

    for dim in dims:
        risk[dim] = structure_report.get(dim, "unknown")

    return {
        "status": "ok",
        "risk_profile": risk,
        "hint": "Ryzyko systemowe ocenione na podstawie struktury pola GSF."
    }
