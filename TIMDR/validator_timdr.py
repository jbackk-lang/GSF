import json

def validate_timdr_continuity(data, schema_path="GSF/TIMDR/map.json"):
    with open(schema_path, "r") as f:
        schema = json.load(f)

    problems = []

    # bardzo uproszczone: sprawdzamy, czy pola w ogóle istnieją
    for field in schema["fields"]:
        if field not in data:
            problems.append(
                f"Brakuje pola '{field}' — ciągłość informacji finansowej jest przerwana."
            )

    return {
        "status": "ok" if not problems else "warning",
        "problems": problems or ["Ciągłość podstawowych pól wygląda na zachowaną."]
    }
