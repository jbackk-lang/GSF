import json

def fieldcore_tensor(data, schema_path="GSF/FIELDCORE/fieldcore_map.json"):
    with open(schema_path, "r") as f:
        schema = json.load(f)

    matrix = schema["influence_matrix"]
    problems = []

    for node in matrix:
        if node not in data:
            problems.append(
                f"Brakuje pola '{node}' — tensor wpływów jest niekompletny."
            )

    return {
        "status": "ok" if not problems else "warning",
        "tensor": matrix,
        "hint": problems or ["Tensor wpływów jest kompletny i spójny."]
    }
